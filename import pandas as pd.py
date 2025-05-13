import pandas as pd
import pandas as pd

csv_file_path1 = 'C:/Users/Praveen Nath/Desktop/merge/output3_file.csv'
csv_file_path2 = 'C:/Users/Praveen Nath/Desktop/merge/procedure.csv'
join_column = 'fhir_patient_id'
output_csv_path = 'C:/Users/Praveen Nath/Desktop/merge/output3_file.csv'

try:
    # Read the CSVs — try with default ',' separator first
    df1 = pd.read_csv(csv_file_path1)
    df2 = pd.read_csv(csv_file_path2, sep=';')  # keep this if you’re sure it’s semicolon-delimited

    # Strip whitespace from column names
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    print("df1 columns:", repr(df1.columns.tolist()))
    print("df2 columns:", repr(df2.columns.tolist()))

    # Merge on 'patient_id'
    merged_df = pd.merge(df1, df2, on=join_column, how='inner')

    merged_df.to_csv(output_csv_path, index=False)
    print(f"\nMerged file saved to: {output_csv_path}")

except FileNotFoundError:
    print("File not found. Check paths.")
except KeyError as e:
    print(f"KeyError: {e}. Column might be missing or misnamed.")
except Exception as e:
    print(f"Other error: {e}")
