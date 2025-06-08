import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings

warnings.filterwarnings('ignore')

# Example of how a script might ensure it can find modules in its parent or project root if needed.
# This might be useful if the script itself needs to import other custom modules from the project.
# current_script_path = os.path.dirname(os.path.abspath(__file__))
# project_root_path = os.path.abspath(os.path.join(current_script_path, '..', '..')) # Adjust depth as needed
# if project_root_path not in sys.path:
#     sys.path.insert(0, project_root_path)

def generated_code_function():
    data_directory_path = r'multi_agents/competition/CarWash_Data'
    import os
    import pandas as pd
    import numpy as np
    
    def analyze_data_quality_and_integrity(data_directory_path):
        files_to_check = ['orders.csv', 'operators.csv', 'customers.csv', 'services.csv', 'transactions.csv']
        dataframes = {}
    
        # Load datasets with error handling
        for file in files_to_check:
            file_path = os.path.join(data_directory_path, file)
            try:
                df = pd.read_csv(file_path)
                dataframes[file] = df
                print(f"Loaded '{file}' successfully: {df.shape[0]} rows, {df.shape[1]} columns.")
            except FileNotFoundError:
                print(f"ERROR: File '{file}' not found in directory '{data_directory_path}'. Skipping.")
            except pd.errors.ParserError:
                print(f"ERROR: Parsing error encountered while reading '{file}'. Skipping.")
            except Exception as e:
                print(f"ERROR: Unexpected error loading '{file}': {e}")
    
        # If no data loaded, exit
        if not dataframes:
            print("No data files loaded. Exiting data quality validation.")
            return
    
        # Function to check nulls and duplicates and print summary
        def check_df_quality(df, df_name):
            print(f"\nData Quality Report for '{df_name}':")
            # Basic info
            print(f" - Shape: {df.shape}")
            print(f" - Columns: {list(df.columns)}")
    
            # Null values
            null_counts = df.isnull().sum()
            null_percent = (null_counts / len(df)) * 100
            null_summary = pd.DataFrame({'null_count': null_counts, 'null_percent': null_percent})
            print(" - Null values per column:")
            print(null_summary[null_summary['null_count'] > 0])
    
            # Duplicate rows
            dup_count = df.duplicated().sum()
            print(f" - Duplicate rows: {dup_count}")
    
            # Unique values per column (for categorical or ID columns)
            unique_counts = df.nunique(dropna=False)
            print(" - Unique values per column:")
            print(unique_counts)
    
            # Data types
            print(" - Data types:")
            print(df.dtypes)
    
        # Run quality checks on each loaded dataframe
        for file, df in dataframes.items():
            check_df_quality(df, file)
    
        # Cross-file basic integrity checks if relevant files exist
        print("\nCross-file Integrity Checks:")
    
        # Example: Check if all operator_ids in orders exist in operators
        if 'orders.csv' in dataframes and 'operators.csv' in dataframes:
            orders = dataframes['orders.csv']
            operators = dataframes['operators.csv']
            missing_ops = set(orders['operator_id'].dropna().unique()) - set(operators['operator_id'].dropna().unique())
            print(f" - Operators referenced in orders but missing in operators.csv: {len(missing_ops)}")
            if len(missing_ops) > 0:
                print(f"   Missing operator_ids sample: {list(missing_ops)[:5]}")
    
        # Check if all customer_ids in orders exist in customers
        if 'orders.csv' in dataframes and 'customers.csv' in dataframes:
            customers = dataframes['customers.csv']
            missing_custs = set(orders['customer_id'].dropna().unique()) - set(customers['customer_id'].dropna().unique())
            print(f" - Customers referenced in orders but missing in customers.csv: {len(missing_custs)}")
            if len(missing_custs) > 0:
                print(f"   Missing customer_ids sample: {list(missing_custs)[:5]}")
    
        # Check for date/time inconsistencies in orders (e.g., order_date before today, or invalid dates)
        if 'orders.csv' in dataframes:
            try:
                orders = dataframes['orders.csv']
                if 'order_date' in orders.columns:
                    orders['order_date_parsed'] = pd.to_datetime(orders['order_date'], errors='coerce')
                    invalid_dates = orders['order_date_parsed'].isna().sum()
                    print(f" - Orders with invalid or missing 'order_date': {invalid_dates}")
    
                    future_dates = (orders['order_date_parsed'] > pd.Timestamp.now()).sum()
                    print(f" - Orders with 'order_date' in the future: {future_dates}")
            except Exception as e:
                print(f"ERROR: Failed datetime validation on orders: {e}")
    
        # Check for negative or zero values in numeric columns where not logical
        for file, df in dataframes.items():
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                for col in numeric_cols:
                    neg_vals = (df[col] < 0).sum()
                    zeros = (df[col] == 0).sum()
                    if neg_vals > 0:
                        print(f" - Negative values found in '{col}' column of '{file}': {neg_vals}")
                    # For zero values, only flag if column likely should not have zeros (e.g., price, duration)
                    if zeros > 0 and any(x in col.lower() for x in ['price','amount','duration','cost']):
                        print(f" - Zero values found in '{col}' column of '{file}': {zeros}")
    
        print("\nData Quality and Integrity Validation Completed.")

if __name__ == "__main__":
    try:
        generated_code_function()
        print('[SCRIPT_EXECUTION_SUCCESS]')
    except Exception as e:
        print(f'[SCRIPT_EXECUTION_ERROR] An error occurred: {str(e)}')
        import traceback
        print(traceback.format_exc())
