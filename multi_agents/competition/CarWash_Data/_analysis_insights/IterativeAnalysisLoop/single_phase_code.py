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
    
    def clean_and_validate_data(data_directory_path):
        # Helper function to load a CSV with error handling
        def load_csv_safe(filename):
            filepath = os.path.join(data_directory_path, filename)
            try:
                df = pd.read_csv(filepath)
                print(f"Loaded '{filename}' successfully with shape {df.shape}.")
                return df
            except FileNotFoundError:
                print(f"Error: File '{filename}' not found in directory '{data_directory_path}'.")
            except pd.errors.ParserError:
                print(f"Error: Parsing error encountered while reading '{filename}'.")
            except Exception as e:
                print(f"Error: Unexpected error reading '{filename}': {e}")
            return None
    
        # Load all relevant data files (assuming typical filenames)
        orders = load_csv_safe('orders.csv')
        operators = load_csv_safe('operators.csv')
        customers = load_csv_safe('customers.csv')
        services = load_csv_safe('services.csv')
        extras = load_csv_safe('extras.csv')
    
        # Store loaded dataframes in a dict for easy iteration and checks
        data_frames = {
            'orders': orders,
            'operators': operators,
            'customers': customers,
            'services': services,
            'extras': extras
        }
    
        # Basic data cleaning and validation
        for name, df in data_frames.items():
            if df is None:
                print(f"Skipping validation for '{name}' as it failed to load.")
                continue
    
            print(f"\n--- Data Validation for '{name}' ---")
            # Check for duplicates
            dup_count = df.duplicated().sum()
            print(f"Duplicate rows: {dup_count}")
            if dup_count > 0:
                print(f"Removing duplicates from '{name}'.")
                df.drop_duplicates(inplace=True)
    
            # Check for missing values summary
            missing = df.isna().sum()
            missing_total = missing.sum()
            print(f"Total missing values: {missing_total}")
            if missing_total > 0:
                print("Missing values per column:")
                print(missing[missing > 0])
    
            # Check for columns with zero variance (constant columns)
            nunique = df.nunique(dropna=False)
            const_cols = nunique[nunique <= 1].index.tolist()
            if const_cols:
                print(f"Columns with zero or one unique value (constant columns): {const_cols}")
    
            # Example specific checks per file
            if name == 'orders':
                # Check for expected columns
                expected_cols = ['order_id', 'customer_id', 'operator_id', 'service_id', 'order_date', 'price', 'status']
                missing_cols = [c for c in expected_cols if c not in df.columns]
                if missing_cols:
                    print(f"Warning: Missing expected columns in orders: {missing_cols}")
    
                # Validate date columns
                if 'order_date' in df.columns:
                    try:
                        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
                        null_dates = df['order_date'].isna().sum()
                        if null_dates > 0:
                            print(f"Warning: {null_dates} invalid/missing dates in 'order_date' column.")
                    except Exception as e:
                        print(f"Error parsing 'order_date': {e}")
    
                # Validate price - should be non-negative
                if 'price' in df.columns:
                    negative_prices = (df['price'] < 0).sum()
                    if negative_prices > 0:
                        print(f"Warning: {negative_prices} orders have negative price values.")
    
            if name == 'operators':
                # Check for unique operator_id
                if 'operator_id' in df.columns:
                    dup_ops = df['operator_id'].duplicated().sum()
                    if dup_ops > 0:
                        print(f"Warning: {dup_ops} duplicated operator_id values.")
    
            if name == 'customers':
                if 'customer_id' in df.columns:
                    dup_cust = df['customer_id'].duplicated().sum()
                    if dup_cust > 0:
                        print(f"Warning: {dup_cust} duplicated customer_id values.")
    
            # Replace original df with cleaned df in dict
            data_frames[name] = df
    
        print("\nData cleaning and validation completed.")
    
        # Return cleaned dataframes dictionary for downstream use if needed
        return data_frames

if __name__ == "__main__":
    try:
        generated_code_function()
        print('[SCRIPT_EXECUTION_SUCCESS]')
    except Exception as e:
        print(f'[SCRIPT_EXECUTION_ERROR] An error occurred: {str(e)}')
        import traceback
        print(traceback.format_exc())
