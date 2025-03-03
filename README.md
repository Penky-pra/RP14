# Meta Patient Builder

A Python tool for extracting and linking patient data from FHIR servers to create meta-patient records.

## Overview

The Meta Patient Builder is designed to extract patient-related data from FHIR servers and build meta-patient records by linking related patient identifiers. This tool is particularly useful for healthcare data integration scenarios where patient records may be fragmented across different systems or identifiers.

## Features

- Extract patient-related resources from FHIR servers
- Build meta-patient records by linking related patient identifiers
- Configurable extraction parameters for different FHIR resource types
- CSV output for easy data analysis and integration

## Requirements

- Python 3.6+
- pandas
- fhir_pyrate (FHIR client library)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd meta-patient-builder

# Install dependencies using uv
uv pip install -r uv.lock
```

## Configuration

The tool uses environment variables for configuration:

- `SEARCH_URL`: FHIR server base URL (default: "http://fhir-server/fhir")
- `FHIR_USER`: Username for FHIR server authentication
- `BASIC_AUTH`: Basic authentication URL
- `REFRESH_AUTH`: Token refresh URL

## Usage

### Basic Usage

```python
from build_meta.meta_patient_builder import SimpleMetaPatientBuilder

# Initialize the builder
builder = SimpleMetaPatientBuilder(
    base_url="https://your-fhir-server.com/fhir",
    output_dir="./output"
)

# Extract encounters
encounters_df, patient_ids = builder.extract_encounters()

# Build meta patients
meta_patients_df = builder.build_meta_patients(patient_ids)
```

### Running the Main Script

```bash
python -m build_meta.meta_patient_builder
```

## Workflow

1. **Extract Encounters**: The tool extracts encounter data from the FHIR server, which includes patient references.
2. **Extract Patient IDs**: From the encounters, unique patient IDs are extracted.
3. **Build Meta Patients**: For each patient ID, the tool queries the FHIR server to find linked patient records.
4. **Output**: The results are stored as CSV files in the specified output directory.

## Customization

### Extracting Different Resource Types

You can use the `default_extraction` method to extract any FHIR resource type:

```python
# Define FHIR paths for extraction
fhir_paths = [
    ("id", "id"),
    ("patient_id", "subject.reference"),
    # Add more paths as needed
]

# Define request parameters
params = {
    "_count": 100,
    # Add more parameters as needed
}

# Extract data
data_df = builder.default_extraction(
    output_name="resource_name",
    resource_type="ResourceType",
    fhir_paths=fhir_paths,
    request_params=params
)
```

## Output

The tool generates CSV files in the specified output directory:
- `encounters.csv`: Contains extracted encounter data
- `meta_patients.csv`: Contains meta-patient records with linked patient IDs

## License

[Specify your license here]

## Contributing

[Specify contribution guidelines here]
