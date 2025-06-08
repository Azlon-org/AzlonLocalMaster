```python
import os
import pandas as pd
import numpy as np

def data_preparation_and_quality_assurance():
    # List all CSV files in the data directory
    try:
        files = [f for f in os.listdir(data_directory_path) if f.endswith('.csv')]
        if not files:
            print("No CSV files found in the data directory.")
            return
    except Exception as e:
        print(f"Error listing files in directory {data_directory_path}: {e}")
        return

    # Dictionary to hold dataframes
    dataframes = {}

    # Load each CSV file with error handling
    for file in files:
        file_path = os.path.join(data_directory_path, file)
        try:
            df = pd.read_csv(file_path)
            dataframes[file] = df
            print(f"Loaded '{file}' successfully with shape {df.shape}.")
        except Exception as e:
            print(f"Failed to load '{file}': {e}")

    # Perform quality checks on each dataframe
    for file, df in dataframes.items():
        print(f"\n=== Data Quality Report for '{file}' ===")

        # Check for missing values
        missing_counts = df.isnull().sum()
        total_missing = missing_counts.sum()
        if total_missing == 0:
            print("No missing values found.")
        else:
            print(f"Missing values detected: {total_missing} total")
            print(missing_counts[missing_counts > 0])

        # Check for duplicate rows
        dup_count = df.duplicated().sum()
        if dup_count == 0:
            print("No duplicate rows found.")
        else:
            print(f"Duplicate rows found: {dup_count}")

        # Basic data type info and conversion suggestions
        print("\nData types:")
        print(df.dtypes)

        # Check numeric columns for outliers using IQR method
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            print("\nOutlier detection (IQR method) for numeric columns:")
            for col in numeric_cols:
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                outlier_count = outliers.shape[0]
                print(f" - {col}: {outlier_count} outliers")

        # Check for inconsistent categorical data (e.g., leading/trailing spaces, case issues)
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            print("\nCategorical columns unique value counts and potential formatting issues:")
            for col in categorical_cols:
                unique_vals = df[col].unique()
                # Check for leading/trailing spaces
                stripped_unique_vals = set([str(val).strip() for val in unique_vals])
                if len(stripped_unique_vals) < len(unique_vals):
                    print(f" - {col}: Possible inconsistent whitespace in categories")
                # Check for case inconsistencies
                lower_unique_vals = set([str(val).lower() for val in unique_vals])
                if len(lower_unique_vals) < len(unique_vals):
                    print(f" - {col}: Possible inconsistent casing in categories")
                print(f"   Unique values count: {len(unique_vals)}")

    print("\nData preparation and quality assurance completed.")
```