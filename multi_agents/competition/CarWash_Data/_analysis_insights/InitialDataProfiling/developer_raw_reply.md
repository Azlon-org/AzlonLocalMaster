```python
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def assess_data_quality_and_integrity(data_directory_path):
    # List of expected data files - adjust if more files are known
    expected_files = ['orders.csv', 'operators.csv', 'customers.csv', 'services.csv']
    loaded_data = {}

    print("Starting data quality and integrity assessment...\n")

    # Load datasets with error handling
    for file in expected_files:
        file_path = os.path.join(data_directory_path, file)
        try:
            df = pd.read_csv(file_path)
            loaded_data[file] = df
            print(f"Loaded '{file}' successfully. Shape: {df.shape}")
        except FileNotFoundError:
            print(f"ERROR: File '{file}' not found in directory '{data_directory_path}'. Skipping.")
        except pd.errors.EmptyDataError:
            print(f"ERROR: File '{file}' is empty. Skipping.")
        except Exception as e:
            print(f"ERROR: Could not load '{file}': {e}")

    print("\n--- Data Quality Reports ---\n")
    for fname, df in loaded_data.items():
        print(f"File: {fname}")
        print("-" * (6 + len(fname)))

        # Basic info
        print("Basic info:")
        buffer = []
        df.info(buf=buffer)
        for line in buffer:
            print(line)
        
        # Summary statistics for numeric columns
        print("\nSummary statistics (numeric columns):")
        print(df.describe().T)

        # Missing values
        missing_counts = df.isnull().sum()
        missing_percent = 100 * missing_counts / len(df)
        missing_df = pd.DataFrame({'missing_count': missing_counts, 'missing_percent': missing_percent})
        missing_df = missing_df[missing_df['missing_count'] > 0].sort_values(by='missing_percent', ascending=False)
        if not missing_df.empty:
            print("\nColumns with missing values:")
            print(missing_df)
        else:
            print("\nNo missing values detected.")

        # Check for duplicated rows
        duplicated_count = df.duplicated().sum()
        print(f"\nDuplicated rows: {duplicated_count}")
        if duplicated_count > 0:
            print("Consider investigating or removing duplicates.")

        # Check for possible anomalies in key columns (if known)
        # For example, dates, IDs, numeric ranges
        # Here we try to guess some columns by name heuristics
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                # Try parsing datetime, count parsing failures
                try:
                    parsed_dates = pd.to_datetime(df[col], errors='coerce')
                    invalid_dates = parsed_dates.isna().sum()
                    if invalid_dates > 0:
                        print(f"Warning: Column '{col}' has {invalid_dates} invalid/missing date entries.")
                except Exception:
                    pass
            if col.lower().endswith('id'):
                # Check uniqueness of IDs
                unique_ids = df[col].nunique(dropna=True)
                total = len(df[col].dropna())
                if unique_ids != total:
                    print(f"Note: Column '{col}' has {unique_ids} unique IDs but {total} total non-null entries.")
            if df[col].dtype in [np.float64, np.int64]:
                # Check for outliers using IQR method
                q1 = df[col].quantile(0.25)
                q3 = df[col].quantile(0.75)
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
                if not outliers.empty:
                    print(f"Column '{col}' has {len(outliers)} potential outliers based on IQR.")

        print("\n")

    # Correlation heatmap for numeric data in 'orders.csv' if loaded
    if 'orders.csv' in loaded_data:
        orders_df = loaded_data['orders.csv']
        numeric_cols = orders_df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 1:
            plt.figure(figsize=(10, 8))
            corr = orders_df[numeric_cols].corr()
            sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f")
            plt.title("Correlation Heatmap of Numeric Features in orders.csv")
            heatmap_path = os.path.join(data_directory_path, 'orders_numeric_correlation_heatmap.png')
            plt.tight_layout()
            plt.savefig(heatmap_path)
            plt.close()
            print(f"Correlation heatmap saved to '{heatmap_path}'")
        else:
            print("Not enough numeric columns in 'orders.csv' to generate correlation heatmap.")

    print("\nData quality and integrity assessment completed.")
```