import os
from dotenv import load_dotenv
import pandas as pd
from fhir_pyrate import Ahoy, Pirate, Miner
from fhir_pyrate.util.fhirobj import FHIRObj
from typing import List, Dict, Optional, Callable

load_dotenv()
def get_procedure_requests(
        df: pd.DataFrame, patient_id_col: str = "fhir_patient_id"
    ) -> pd.DataFrame:
    """Function for retrieving Procedure information.

    Args:
        df (pd.DataFrame): DataFrame containing patients.
        patient_id_col (str, optional): Column specifying the unique patient identifier. Defaults to "fhir_patient_id".

    Returns:
        pd.DataFrame: DataFrame with Procedure information about each patient.
    """

    def _process_func(bundle: FHIRObj) -> List[Dict[str, str]]:
        """Helper function to extract the procedure information from a FHIR bundle.

        Args:
            bundle (FHIRObj): FHIR-PYrate bundle object.

        Returns:
            List[Dict[str, str]]: List of dictionaries containing procedure details.
        """
        records = []
        for entry in bundle.entry or []:
            resource = entry.resource

            records.append(
                {
                    "fhir_patient_id": resource.subject.reference.split("/")[-1],
                    "procedure_id": resource.id,
                    "procedure_status": resource.status if hasattr(resource, "status") else None,
                    "procedure_code": resource.code.coding[0].code
                    if resource.code and resource.code.coding else None,
                    "procedure_display": resource.code.coding[0].display
                    if resource.code and resource.code.coding else None,
                    "performed_date": getattr(resource, "performedDateTime", None),
                    "performed_period_start": getattr(resource.performedPeriod, "start", None)
                    if hasattr(resource, "performedPeriod") else None,
                    "performed_period_end": getattr(resource.performedPeriod, "end", None)
                    if hasattr(resource, "performedPeriod") else None,
                }
            )
            # todo save csv here.
            #  records.to_csv('procedure_tmp.csv') but the records are a list of something that needs to be handled differently. fix it please.
        return records

    # Ensure unique patient IDs
    df = df.drop_duplicates(subset=[patient_id_col])

    # Use FHIR-PYrate to fetch Procedure resources
    df_procedure_requests = search.trade_rows_for_dataframe(
        df=df,
        resource_type="Procedure",
        request_params={
            "_count": "500",
            "_sort": "_id",
            "class": "IMP",
        },
        df_constraints={
            "subject": patient_id_col,
            #"date": [("ge", 2016-01-01), ("le", 2023-01-01)],
        },
        with_ref=True,
        process_function=_process_func,
    )

    return df_procedure_requests
def get_observation_requests(
        df: pd.DataFrame, patient_id_col: str = "fhir_patient_id"
    ) -> pd.DataFrame:
    """Function for retrieving Observation information.

    Args:
        df (pd.DataFrame): DataFrame containing patients.
        patient_id_col (str, optional): Column specifying the unique patient identifier. Defaults to "fhir_patient_id".

    Returns:
        pd.DataFrame: DataFrame with Observation information about each patient.
    """

    def _process_func(bundle: FHIRObj) -> List[Dict[str, str]]:
        """Helper function to extract the observation information from a FHIR bundle.

        Args:
            bundle (FHIRObj): FHIR-PYrate bundle object.

        Returns:
            List[Dict[str, str]]: List of dictionaries containing observation details.
        """
        records = []
        for entry in bundle.entry or []:
            resource = entry.resource

            records.append(
                {
                    "fhir_patient_id": resource.subject.reference.split("/")[-1],
                    "observation_id": resource.id,
                    "observation_status": resource.status if hasattr(resource, "status") else None,
                    "observation_code": resource.code.coding[0].code
                    if resource.code and resource.code.coding else None,
                    "observation_display": resource.code.coding[0].display
                    if resource.code and resource.code.coding else None,
                    "effective_date": getattr(resource, "effectiveDateTime", None),
                    "effective_period_start": getattr(resource.effectivePeriod, "start", None)
                    if hasattr(resource, "effectivePeriod") else None,
                    "effective_period_end": getattr(resource.effectivePeriod, "end", None)
                    if hasattr(resource, "effectivePeriod") else None,
                    #"value": getattr(resource, "valueQuantity", {}).get("value", None)
                    #if hasattr(resource, "valueQuantity") else None,
                #"unit": getattr(resource, "valueQuantity", {}).get("unit", None)
                    #if hasattr(resource, "valueQuantity") else None,
                }
            )
        return records

    # Ensure unique patient IDs
    df = df.drop_duplicates(subset=[patient_id_col])

    # Use FHIR-PYrate to fetch Observation resources
    df_observation_requests = search.trade_rows_for_dataframe(
        df=df,
        resource_type="Observation",
        request_params={
            "_count": "500",
            "_sort": "_id",
        },
        df_constraints={
            "subject": patient_id_col,
            #"date": [("ge", "2016-01-01"), ("le", "2023-01-01")],
        },
        with_ref=True,
        process_function=_process_func,
    )

    return df_observation_requests

def get_diagnoses(
        df: pd.DataFrame, patient_id_col: str = "fhir_patient_id"
    ) -> pd.DataFrame:
    """
    Function to retrieve Diagnosis information for patients. Mainly used for melanoma cohort analysis.

    Args:
        df (pd.DataFrame): DataFrame containing patients.
        patient_id_col (str, optional): Column specifying the unique patient identifier. Defaults to "fhir_patient_id".

    Returns:
        pd.DataFrame: DataFrame with Diagnosis information for each patient.
    """

    def _process_func(bundle: FHIRObj) -> List[Dict[str, str]]:
        """
        Helper function to extract the diagnosis information from a FHIR bundle.

        Args:
            bundle (FHIRObj): FHIR-PYrate bundle object.

        Returns:
            List[Dict[str, str]]: List of dictionaries containing the patient id, diagnosis id, and diagnosis details.
        """
        records = []
        for entry in bundle.entry or []:
            resource = entry.resource

            records.append(
                {
                    "fhir_patient_id": resource.subject.reference.split("/")[-1],
                    "diagnosis_id": resource.id,
                    #"icd_10_code": resource.condition[0].coding[0].code,
                    "icd_10_display": resource.condition[0].coding[0].display,
                    "onset_date": resource.onsetDateTime,  # Onset of the condition
                    "recorded_date": resource.recordedDate,  # When the diagnosis was recorded
                    "severity": resource.severity.coding[0].display
                    if resource.severity else None,  # Severity if available
                    "clinical_status": resource.clinicalStatus.coding[0].display
                    if resource.clinicalStatus else None,
                    "verification_status": resource.verificationStatus.coding[0].display
                    if resource.verificationStatus else None,
                }
            )

        return records

    # Ensure patient list is unique
    df = df.drop_duplicates(subset=[patient_id_col])

    # Retrieve diagnosis data
    df_diagnoses = search.trade_rows_for_dataframe(
        df,
        resource_type="Condition",  # Diagnosis often falls under the Condition resource in FHIR
        request_params={
            "_count": "500",
            "_sort": "_id",
            #"date": "ge2019-01-01"  # Include only diagnoses recorded on or after January 1, 2019
        },
        df_constraints={
            "subject": patient_id_col,
        },
        with_ref=False,
        process_function=_process_func,
    )

    return df_diagnoses

    
def get_all_melanoma_patients() -> pd.DataFrame:
        """Function to retrieve all patients that were diagnosed with an ICD C43.0 - C43-1 code.

        Returns:
            pd.DataFrame: DataFrame containing identified patients.
        """

        def _process_func(bundle: FHIRObj) -> List[Dict]:
            """Helper function to extract the unique identifier, and diagnosis information.

            Args:
                bundle (FHIRObj): FHIR bundle containing entries that should be parsed.

            Returns:
                List[Dict]: List with results.
            """
            records = []
            for entry in bundle.entry or []:
                resource = entry.resource

                records.append(
                    {
                        "fhir_patient_id": resource.subject.reference.split("/")[-1],
                        "icd_10_display": resource.code.coding[0].display,
                        "icd_10_system": resource.code.coding[0].system,
                        "condition_diagnosis_date": resource.recordedDate,
                    }
                )
            return records

        # Define ICD Code range for C43 (Melanoma)
        icd_10_values = ["C43." + str(i) for i in range(10)]
        data = {"icd_10": icd_10_values}
        condition_df = pd.DataFrame(data)

        print(
            f"The following ICD-10 codes will be used for the search:\n {icd_10_values}"
        )

        condition_patient_df = search.trade_rows_for_dataframe(
            df=condition_df,
            resource_type="Condition",
            request_params={
                "_sort": "_id",
                "_count": 100,
                #"authoredon": "ge2019-01-01", 
            },
            with_ref=True,
            df_constraints={
                "code": ("http://fhir.de/CodeSystem/dimdi/icd-10-gm%7C", "icd_10")
            },
            process_function=_process_func,
        )

        print(condition_patient_df)
        
        condition_patient_df = condition_patient_df.sort_values(
            by=["condition_diagnosis_date"]
        )
        condition_patient_df = condition_patient_df.drop_duplicates(
            subset=["fhir_patient_id"], keep="first"
        )

        return condition_patient_df


print(os.environ['CONDA_DEFAULT_ENV'])
auth = Ahoy(
            auth_type="token",
            auth_method="env",
            auth_url=os.getenv("AUTH_URL"),
            refresh_url=os.getenv("AUTH_URL"),
            username=os.getenv("FHIR_USER"),
        )

search = Pirate(
            auth=auth,
            base_url=os.getenv("BASE_URL"),
            print_request_url=True,
            num_processes=1,
        )
#df_condition = get_all_melanoma_patients()
#df_condition.to_csv('Condition.csv')
#print(df_condition)
df_diagnosis = get_all_melanoma_patients()
df_diagnosis.to_csv('Diagnosis.csv')
print(df_diagnosis)
#df_procedure = get_procedure_requests(df=df_diagnosis, patient_id_col= "fhir_patient_id")
#df_procedure.to_csv('procedure.csv')
#print(df_procedure)
#df_encounters = get_encounters(df=df_diagnosis, patient_id_col= "fhir_patient_id")
#df_encounters.to_csv('encounter.csv')
#print(df_encounters)
df_observation= get_observation_requests(df=df_diagnosis, patient_id_col="fhir_patient_id")
df_observation.to_csv('observation.csv')
print(df_observation)
df_medications = get_medication_requests(df=df_diagnosis, patient_id_col="fhir_patient_id")
df_medications.to_csv('medications.csv')
print(df_medications)
df_diagnosis = get_diagnoses(df=df_diagnosis, patient_id_col="fhir_patient_id")  
df_diagnosis.to_csv('diagnosis.csv')
print(df_diagnosis)
