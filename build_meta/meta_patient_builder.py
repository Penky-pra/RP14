import os
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Union, Tuple, Optional, Sequence
from fhir_pyrate import Ahoy
from fhir_pyrate.pirate import Pirate

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Helper functions
def extract_id(id_str):
    """Extract ID from a FHIR reference."""
    if isinstance(id_str, str) and "/" in id_str:
        return id_str.split("/")[-1]
    return id_str


def store_df(df, output_path, resource_name):
    """Store DataFrame as CSV file."""
    logger.info(f"Storing {resource_name} data with {len(df)} rows to {output_path}")
    df.reset_index(drop=True).to_csv(output_path, index=False)


class SimpleMetaPatientBuilder:
    def __init__(self, base_url=None, output_dir="./output"):
        """
        Initialize the SimpleMetaPatientBuilder.

        Parameters:
        - base_url: The FHIR server base URL (defaults to environment variable)
        - output_dir: Directory to store output files
        """
        # Use environment variables if parameters not provided
        self.base_url = base_url or os.environ.get(
            "SEARCH_URL", "http://fhir-server/fhir"
        )

        # Setup authentication
        self.auth = Ahoy(
            auth_method="env",
            username=os.environ.get("FHIR_USER", ""),
            auth_url=os.environ.get("BASIC_AUTH", ""),
            refresh_url=os.environ.get("REFRESH_AUTH", ""),
        )

        # Initialize Pirate
        self.search = Pirate(
            auth=self.auth,
            base_url=self.base_url,
            num_processes=30,
            print_request_url=False,
        )

        # Create output directory
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def default_extraction(
        self,
        output_name: str,
        resource_type: str,
        fhir_paths: Sequence[Union[str, Tuple[str, str]]],
        request_params: Optional[Dict[str, str]] = None,
        limit: int = 10,
    ):
        """
        Generic extraction method for FHIR resources.

        Parameters:
        - output_name: Name for the output file
        - resource_type: FHIR resource type
        - fhir_paths: List of tuples (column_name, fhir_path)
        - request_params: Additional request parameters

        Returns:
        - DataFrame containing the extracted data
        """
        logger.info(f"Extracting {resource_type} data")

        output_path = self.output_dir / f"{output_name}.csv"

        # Set up request parameters
        if request_params is None:
            request_params = {}

        request_params["_count"] = str(limit)

        # Use steal_bundles_to_dataframe for simple extraction
        result = self.search.steal_bundles_to_dataframe(
            resource_type=resource_type,
            request_params=request_params,
            fhir_paths=list(fhir_paths),
        )

        # Convert result to DataFrame if it's a dictionary
        if isinstance(result, dict):
            df = pd.DataFrame()
            for key, value in result.items():
                if isinstance(value, pd.DataFrame) and not value.empty:
                    df = value
                    break
        else:
            df = result

        if df.empty:
            logger.warning(f"No {resource_type} data found")
            return df

        # Store the data
        store_df(df, output_path, resource_type)

        return df

    def extract_encounters(self):
        """
        Extract encounters from the FHIR server.

        Parameters:
        - limit: Maximum number of encounters to retrieve

        Returns:
        - DataFrame containing encounter data and list of patient IDs
        """
        # Define FHIR paths for encounter extraction
        fhir_paths = [
            ("encounter_id", "id"),
            ("patient_id", "subject.reference.replace('Patient/', '')"),
            ("status", "status"),
            ("class_code", "class.code"),
            ("class_display", "class.display"),
            ("type_code", "type[0].coding[0].code"),
            ("type_display", "type[0].coding[0].display"),
            ("start_date", "period.start"),
            ("end_date", "period.end"),
        ]

        # Restore encounter parameters
        # TODO: Change this to your needs...
        encounter_params = {
            "_count": 5000,
            "_sort": "-date",
            "subject": "000324ea9922d3e6089d85febef322308aa07d1ce565064aa4b2341fa7dd4cbc",
        }

        # Extract encounters
        encounters_df = self.default_extraction(
            output_name="encounters",
            resource_type="Encounter",
            fhir_paths=fhir_paths,
            request_params=encounter_params,
        )

        if encounters_df.empty:
            logger.warning("No encounters found")
            return encounters_df, []

        # Extract unique patient IDs
        patient_ids = encounters_df["patient_id"].unique().tolist()
        logger.info(f"Found {len(patient_ids)} unique patients in encounters")

        return encounters_df, patient_ids

    def build_meta_patients(self, patient_ids: List[str]):
        """
        Build meta patients for the given patient IDs.

        Parameters:
        - patient_ids: List of patient IDs

        Returns:
        - DataFrame containing meta patient data
        """
        logger.info(f"Building meta patients for {len(patient_ids)} patients")

        # Create a DataFrame with patient IDs
        patient_ids_unique = list(set(patient_ids))  # Convert to set and back to list
        patients_df = pd.DataFrame({"patient_id": patient_ids_unique})

        # Use trade_rows_for_dataframe to get linked patients
        try:
            result = self.search.trade_rows_for_dataframe(
                df=patients_df,
                df_constraints={"link": "patient_id"},
                resource_type="Patient",
                fhir_paths=[
                    ("linked_patient_id", "link.other.reference"),
                    ("meta_patient", "id"),
                    ("birth_date", "birthDate"),
                    ("sex", "gender"),
                    ("deceased_date", "deceasedDateTime"),
                ],
                with_ref=True,
            )

            # Convert result to DataFrame if it's a dictionary
            if isinstance(result, dict):
                meta_patients_df = pd.DataFrame()
                for key, value in result.items():
                    if isinstance(value, pd.DataFrame) and not value.empty:
                        meta_patients_df = value
                        break
            else:
                meta_patients_df = result

            # Process the DataFrame
            if (
                not meta_patients_df.empty
                and "linked_patient_id" in meta_patients_df.columns
            ):
                # Explode linked_patient_id and clean up references
                meta_patients_df = meta_patients_df.explode("linked_patient_id")
                meta_patients_df["linked_patient_id"] = meta_patients_df[
                    "linked_patient_id"
                ].apply(lambda x: extract_id(x) if pd.notna(x) else None)

            # For patients without links, use their own ID as linked_patient_id
            if "linked_patient_id" not in meta_patients_df.columns:
                meta_patients_df["linked_patient_id"] = meta_patients_df["patient_id"]
            else:
                meta_patients_df["linked_patient_id"] = meta_patients_df.apply(
                    lambda x: x.linked_patient_id
                    if pd.notna(x.linked_patient_id)
                    else x.patient_id,
                    axis=1,
                )

        except Exception as e:
            logger.error(f"Error building meta patients: {e}")
            # Fallback: create a simple DataFrame with self-links
            meta_patients_df = patients_df.copy()
            meta_patients_df["linked_patient_id"] = meta_patients_df["patient_id"]
            meta_patients_df["meta_patient"] = meta_patients_df["patient_id"]

        # Store meta patients
        meta_patient_path = self.output_dir / "meta_patients.csv"
        store_df(meta_patients_df, meta_patient_path, "meta_patients")

        return meta_patients_df


def main():
    """
    Main function to demonstrate the workflow.

    Workflow:
    1. Extract encounters
    2. Build meta patients for the patient IDs from these encounters
    """
    # Initialize builder
    builder = SimpleMetaPatientBuilder()

    # Step 1: Extract encounters (this cloud be any resouce)
    encounters_df, patient_ids = builder.extract_encounters()
    logger.info(
        f"Extracted {len(encounters_df)} encounters for {len(patient_ids)} patients"
    )

    if not patient_ids:
        logger.warning("No patient IDs found in encounters, cannot proceed")
        return pd.DataFrame()

    # Step 2: Build meta patients
    meta_patients_df = builder.build_meta_patients(patient_ids)
    logger.info(f"Built {len(meta_patients_df)} meta patient records")

    # Now you can use meta_patients_df for further processing
    # Just do an inner join with the meta_patients_df on linked_patient_id and patient_id of whatever df you have
    # Now you can loop through meta_patient and do whatever...


if __name__ == "__main__":
    main()
