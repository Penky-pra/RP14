import os
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Union, Tuple, Optional, Sequence
from fhir_pyrate import Ahoy
from fhir_pyrate.pirate import Pirate
from dotenv import load_dotenv
import time  # Import the time module for measuring execution time

load_dotenv()  # Load variables from .env file

FHIR_USER = os.getenv("FHIR_USER")
if not FHIR_USER:
    raise EnvironmentError("FHIR_USER is not set. Check your environment variables or .env file.")

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
    def __init__(self, base_url=None, output_dir="./output", num_processes=20, resources_per_page=750, is_initial_test=False):
        """
        Initialize the SimpleMetaPatientBuilder.

        Parameters:
        - base_url: The FHIR server base URL (defaults to environment variable)
        - output_dir: Directory to store output files
        - num_processes: Number of parallel processes for FHIR requests (adjusted default)
        - resources_per_page: Number of resources to request per page (_count parameter) (adjusted default)
        - is_initial_test: Flag for limiting initial extraction for testing
        """
        # Use environment variables if parameters not provided
        self.base_url = base_url or os.environ.get(
            "SEARCH_URL", "http://fhir-server/fhir"
        )
        self.num_processes = num_processes
        self.resources_per_page = resources_per_page
        self.is_initial_test = is_initial_test

        # Setup authentication
        self.auth = Ahoy(
            auth_method="env",
            username=os.environ.get("FHIR_USER", "parnath"),
            auth_url=os.environ.get("BASIC_AUTH", "https://ship.ume.de/app/Auth/v1/basicAuth"),
            refresh_url=os.environ.get("REFRESH_AUTH", "https://ship.ume.de/app/Auth/v1/refresh"),
        )

        # Initialize Pirate
        self.search = Pirate(
            auth=self.auth,
            base_url=self.base_url,
            num_processes=self.num_processes,
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
        limit: int = 10,  # This limit might be overridden by resources_per_page
    ):
        """
        Generic extraction method for FHIR resources.
        """
        logger.info(f"Extracting {resource_type} data")
        start_time = time.time()
        output_path = self.output_dir / f"{output_name}.csv"

        # Set up request parameters
        if request_params is None:
            request_params = {}

        request_params["_count"] = str(self.resources_per_page)

        # --- Potential initial limit for testing ---
        if self.is_initial_test:
            request_params["_count"] = "100"

        try:
            result = self.search.steal_bundles_to_dataframe(
                resource_type=resource_type,
                request_params=request_params,
                fhir_paths=list(fhir_paths),
            )

            # Convert result to DataFrame
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
                return df, []  # Return empty list for patient IDs

            # Extract patient IDs if the resource has a subject
            patient_ids = []
            if "subject.reference.replace('Patient/', '')" in [path for _, path in fhir_paths]:
                patient_ids = df["patient_id"].unique().tolist()
                logger.info(f"Found {len(patient_ids)} unique patients in {resource_type}")

            # Store the data
            store_df(df, output_path, resource_type)
            end_time = time.time()
            logger.info(f"Finished extracting {resource_type} in {end_time - start_time:.2f} seconds.")
            return df, patient_ids

        except Exception as e:
            logger.error(f"Error during extraction of {resource_type}: {e}")
            return pd.DataFrame(), []

    def extract_procedures(self):
        """Extract procedures from the FHIR server."""
        fhir_paths = [
            ("procedure_id", "id"),
            ("patient_id", "subject.reference.replace('Patient/', '')"),
            ("status", "status"),
            ("code_code", "code.coding[0].code"),
            ("code_display", "code.coding[0].display"),
            ("performed_date_time", "performedDateTime"),
        ]
        procedure_params = {}
        return self.default_extraction(
            output_name="procedures",
            resource_type="Procedure",
            fhir_paths=fhir_paths,
            request_params=procedure_params,
        )

    def extract_observations(self):
        """Extract observations from the FHIR server."""
        fhir_paths = [
            ("observation_id", "id"),
            ("patient_id", "subject.reference.replace('Patient/', '')"),
            ("status", "status"),
            ("code_code", "code.coding[0].code"),
            ("code_display", "code.coding[0].display"),
            ("effective_date_time", "effectiveDateTime"),
            ("value_quantity", "valueQuantity.value"),
            ("value_unit", "valueQuantity.unit"),
        ]
        observation_params = {}
        return self.default_extraction(
            output_name="observations",
            resource_type="Observation",
            fhir_paths=fhir_paths,
            request_params=observation_params,
        )

    def extract_diagnoses(self):
        """Extract diagnoses (Condition resources) from the FHIR server."""
        fhir_paths = [
            ("diagnosis_id", "id"),
            ("patient_id", "subject.reference.replace('Patient/', '')"),
            ("clinical_status", "clinicalStatus.coding[0].display"),
            ("verification_status", "verificationStatus.coding[0].display"),
            ("code_code", "code.coding[0].code"),
            ("code_display", "code.coding[0].display"),
            ("onset_date_time", "onsetDateTime"),
        ]
        diagnosis_params = {}
        return self.default_extraction(
            output_name="diagnoses",
            resource_type="Condition",  # Condition is used for diagnoses
            fhir_paths=fhir_paths,
            request_params=diagnosis_params,
        )

    def extract_medications(self):
        """Extract Medication resources from the FHIR server."""
        fhir_paths = [
            ("medication_id", "id"),
            ("code_code", "code.coding[0].code"),
            ("code_display", "code.coding[0].display"),
            ("form_code", "form.coding[0].code"),
            ("form_display", "form.coding[0].display"),
        ]
        medication_params = {}  # Medications don't directly link to a patient in the same way
        return self.default_extraction(
            output_name="medications",
            resource_type="Medication",
            fhir_paths=fhir_paths,
            request_params=medication_params,
        )

    def extract_medication_statements(self):
        """
        Extract medication statements from the FHIR server.
        **Consider adding filters here for performance.**
        """
        fhir_paths = [
            ("medication_statement_id", "id"),
            ("patient_id", "subject.reference.replace('Patient/', '')"),
            ("status", "status"),
            ("effective_date_time", "effectiveDateTime"),
            ("medication_code", "medicationCodeableConcept.coding[0].code"),
            ("medication_display", "medicationCodeableConcept.coding[0].display"),
            ("dosage_instruction", "dosage[0].text"),
        ]
        medication_statement_params = {
            "_count": self.resources_per_page,
            # Add filters based on your needs and server capabilities:
            # "effectiveDateTime": "gt2024-01-01",
            # "status": "active",
            # "patient": "Patient/some-patient-id",
        }
        return self.default_extraction(
            output_name="medication_statements",
            resource_type="MedicationStatement",
            fhir_paths=fhir_paths,
            request_params=medication_statement_params,
        )

    def build_meta_patients(self, patient_ids: List[str]):
        """
        Build meta patients for the given patient IDs.
        """
        logger.info(f"Building meta patients for {len(patient_ids)} patients")
        start_time = time.time()
        patient_ids_unique = list(set(patient_ids))  # Ensure uniqueness
        patients_df = pd.DataFrame({"patient_id": patient_ids_unique})

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
            # Process the result into meta_patients_df (as before)
            if isinstance(result, dict):
                meta_patients_df = pd.DataFrame()
                for key, value in result.items():
                    if isinstance(value, pd.DataFrame) and not value.empty:
                        meta_patients_df = value
                        break
            else:
                meta_patients_df = result

            if not meta_patients_df.empty and "linked_patient_id" in meta_patients_df.columns:
                meta_patients_df = meta_patients_df.explode("linked_patient_id")
                meta_patients_df["linked_patient_id"] = meta_patients_df["linked_patient_id"].apply(
                    lambda x: extract_id(x) if pd.notna(x) else None
                )
            elif not meta_patients_df.empty:
                meta_patients_df["linked_patient_id"] = meta_patients_df["patient_id"]
                meta_patients_df["meta_patient"] = meta_patients_df["patient_id"]
            else:
                meta_patients_df = pd.DataFrame()  # Empty DataFrame if no results

        except Exception as e:
            logger.error(f"Error building meta patients: {e}")
            meta_patients_df = pd.DataFrame()  # Return empty DataFrame on error

        # Store meta patients
        meta_patient_path = self.output_dir / "meta_patients.csv"
        if not meta_patients_df.empty:
            store_df(meta_patients_df, meta_patient_path, "meta_patients")
        else:
            logger.warning("No meta-patient data to store.")

        end_time = time.time()
        logger.info(f"Finished building meta patients in {end_time - start_time:.2f} seconds.")
        return meta_patients_df


def main():
    """
    Main function to demonstrate the workflow for various resources.
    """
    start_time = time.time()
    # Initialize builder with adjusted num_processes and resources_per_page
    builder = SimpleMetaPatientBuilder(num_processes=20, resources_per_page=750, is_initial_test=False)
    # builder = SimpleMetaPatientBuilder(num_processes=5, resources_per_page=100, is_initial_test=True) # For initial testing

    # Extract resources
    procedures_df, procedure_patient_ids = builder.extract_procedures()
    observations_df, observation_patient_ids = builder.extract_observations()
    diagnoses_df, diagnosis_patient_ids = builder.extract_diagnoses()
    medications_df, _ = builder.extract_medications()
    medication_statements_df, medication_statement_patient_ids = builder.extract_medication_statements()

    # Combine all patient IDs (ensure uniqueness)
    all_patient_ids = list(set(
        procedure_patient_ids + observation_patient_ids + diagnosis_patient_ids + medication_statement_patient_ids
    ))
    logger.info(f"Found {len(all_patient_ids)} unique patients across all patient-linked resources")

    if all_patient_ids:
        # Build meta patients
        meta_patients_df = builder.build_meta_patients(all_patient_ids)

        # Merge the extracted data with meta patients
        if not procedures_df.empty and not meta_patients_df.empty:
            merged_procedures_df = pd.merge(
                procedures_df, meta_patients_df, how="inner", left_on="patient_id", right_on="linked_patient_id", suffixes=('_procedure', '_meta_patient')
            )
            store_df(merged_procedures_df, builder.output_dir / "procedures_with_meta_patients.csv", "procedures_with_meta_patients")

        if not observations_df.empty and not meta_patients_df.empty:
            merged_observations_df = pd.merge(
                observations_df, meta_patients_df, how="inner", left_on="patient_id", right_on="linked_patient_id", suffixes=('_observation', '_meta_patient')
            )
            store_df(merged_observations_df, builder.output_dir / "observations_with_meta_patients.csv", "observations_with_meta_patients")

        if not diagnoses_df.empty and not meta_patients_df.empty:
            merged_diagnoses_df = pd.merge(
                diagnoses_df, meta_patients_df, how="inner", left_on="patient_id", right_on="linked_patient_id", suffixes=('_diagnosis', '_meta_patient')
            )
            store_df(merged_diagnoses_df, builder.output_dir / "diagnoses_with_meta_patients.csv", "diagnoses_with_meta_patients")

        if not medication_statements_df.empty and not meta_patients_df.empty:
            merged_medication_statements_df = pd.merge(
                medication_statements_df, meta_patients_df, how="inner", left_on="patient_id", right_on="linked_patient_id", suffixes=('_medication_statement', '_meta_patient')
            )
            store_df(merged_medication_statements_df, builder.output_dir / "medication_statements_with_meta_patients.csv", "medication_statements_with_meta_patients")

    else:
        logger.warning("No patient IDs found, skipping meta-patient building and merging.")

    end_time = time.time()
    logger.info(f"Total execution time: {end_time - start_time:.2f} seconds.")


if __name__ == "__main__":
    main()