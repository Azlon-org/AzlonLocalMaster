```python
import os
import pandas as pd
import numpy as np

def repair_and_validate_datasets(data_directory_path):
    # Helper function to load CSV with error handling
    def load_csv(file_name):
        path = os.path.join(data_directory_path, file_name)
        try:
            df = pd.read_csv(path)
            print(f"Loaded {file_name} with shape {df.shape}")
            return df
        except FileNotFoundError:
            print(f"Error: {file_name} not found in {data_directory_path}")
            return None
        except pd.errors.ParserError:
            print(f"Error: Parsing {file_name} failed - possible corruption or malformed CSV.")
            return None
        except Exception as e:
            print(f"Error loading {file_name}: {e}")
            return None

    # Helper function to detect and report missing values and duplicates
    def data_overview(df, name):
        if df is None:
            print(f"Skipping overview for {name} - dataframe not loaded.")
            return
        print(f"\n--- Data Overview: {name} ---")
        print(f"Columns: {df.columns.tolist()}")
        print(f"Shape: {df.shape}")
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(f"Missing values per column:\n{missing[missing > 0]}")
        else:
            print("No missing values detected.")
        dup_count = df.duplicated().sum()
        print(f"Duplicate rows: {dup_count}")

    # Helper function to attempt basic repairs
    def repair_df(df, name):
        if df is None:
            return None

        # Remove fully duplicate rows
        before = df.shape[0]
        df = df.drop_duplicates()
        after = df.shape[0]
        if before != after:
            print(f"{name}: Removed {before - after} duplicate rows.")

        # For critical columns, we try to fix types and fill missing if possible
        # We'll define some common fixes per dataset below

        # Repair based on dataset name
        if name == 'clients.csv':
            # Expect client_id as primary key - drop rows missing it
            if 'client_id' in df.columns:
                before = df.shape[0]
                df = df.dropna(subset=['client_id'])
                after = df.shape[0]
                if before != after:
                    print(f"{name}: Dropped {before - after} rows with missing client_id.")
                # Try to convert client_id to int if not already
                df['client_id'] = pd.to_numeric(df['client_id'], errors='coerce')
                before = df.shape[0]
                df = df.dropna(subset=['client_id'])
                df['client_id'] = df['client_id'].astype(int)
                after = df.shape[0]
                if before != after:
                    print(f"{name}: Dropped {before - after} rows with non-numeric client_id.")
            # Fill missing categorical info with 'Unknown' if any
            for col in df.select_dtypes(include='object').columns:
                if df[col].isnull().any():
                    df[col] = df[col].fillna('Unknown')

        elif name == 'orders.csv':
            # Expect order_id, client_id, operator_id, order_date, status, price etc.
            # Drop rows missing order_id or client_id or operator_id
            critical_cols = ['order_id', 'client_id', 'operator_id']
            for c in critical_cols:
                if c in df.columns:
                    before = df.shape[0]
                    df = df.dropna(subset=[c])
                    after = df.shape[0]
                    if before != after:
                        print(f"{name}: Dropped {before - after} rows with missing {c}.")
                    # Convert IDs to int
                    df[c] = pd.to_numeric(df[c], errors='coerce')
                    before = df.shape[0]
                    df = df.dropna(subset=[c])
                    df[c] = df[c].astype(int)
                    after = df.shape[0]
                    if before != after:
                        print(f"{name}: Dropped {before - after} rows with non-numeric {c}.")
            # Parse order_date to datetime if exists
            if 'order_date' in df.columns:
                df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
                missing_dates = df['order_date'].isnull().sum()
                if missing_dates > 0:
                    print(f"{name}: Found {missing_dates} invalid order_date entries, dropping those rows.")
                    df = df.dropna(subset=['order_date'])
            # Price column: convert to numeric and fill missing or invalid with 0
            if 'price' in df.columns:
                df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
                # Replace negative prices with 0 (invalid)
                neg_prices = (df['price'] < 0).sum()
                if neg_prices > 0:
                    print(f"{name}: Found {neg_prices} negative prices, setting to 0.")
                    df.loc[df['price'] < 0, 'price'] = 0

        elif name == 'operators.csv':
            # Expect operator_id as primary key
            if 'operator_id' in df.columns:
                before = df.shape[0]
                df = df.dropna(subset=['operator_id'])
                after = df.shape[0]
                if before != after:
                    print(f"{name}: Dropped {before - after} rows with missing operator_id.")
                df['operator_id'] = pd.to_numeric(df['operator_id'], errors='coerce')
                before = df.shape[0]
                df = df.dropna(subset=['operator_id'])
                df['operator_id'] = df['operator_id'].astype(int)
                after = df.shape[0]
                if before != after:
                    print(f"{name}: Dropped {before - after} rows with non-numeric operator_id.")
            # Fill missing categorical with 'Unknown'
            for col in df.select_dtypes(include='object').columns:
                if df[col].isnull().any():
                    df[col] = df[col].fillna('Unknown')

        elif name == 'operator_balance.csv':
            # Expect operator_id, balance, last_update_date
            if 'operator_id' in df.columns:
                df['operator_id'] = pd.to_numeric(df['operator_id'], errors='coerce')
                before = df.shape[0]
                df = df.dropna(subset=['operator_id'])
                df['operator_id'] = df['operator_id'].astype(int)
                after = df.shape[0]
                if before != after:
                    print(f"{name}: Dropped {before - after} rows with invalid operator_id.")
            if 'balance' in df.columns:
                df['balance'] = pd.to_numeric(df['balance'], errors='coerce').fillna(0)
            if 'last_update_date' in df.columns:
                df['last_update_date'] = pd.to_datetime(df['last_update_date'], errors='coerce')
                missing_dates = df['last_update_date'].isnull().sum()
                if missing_dates > 0:
                    print(f"{name}: Found {missing_dates} invalid last_update_date entries, dropping those rows.")
                    df = df.dropna(subset=['last_update_date'])

        elif name == 'activity_logs.csv':
            # Expect activity_id, operator_id, activity_type, timestamp, details
            if 'activity_id' in df.columns:
                before = df.shape[0]
                df = df.dropna(subset=['activity_id'])
                after = df.shape[0]
                if before != after:
                    print(f"{name}: Dropped {before - after} rows with missing activity_id.")
                df['activity_id'] = pd.to_numeric(df['activity_id'], errors='coerce')
                before = df.shape[0]
                df = df.dropna(subset=['activity_id'])
                df['activity_id'] = df['activity_id'].astype(int)
                after = df.shape[0]
                if before != after:
                    print(f"{name}: Dropped {before - after} rows with non-numeric activity_id.")
            if 'operator_id' in df.columns:
                df['operator_id'] = pd.to_numeric(df['operator_id'], errors='coerce')
                before = df.shape[0]
                df = df.dropna(subset=['operator_id'])
                df['operator_id'] = df['operator_id'].astype(int)
                after = df.shape[0]
                if before != after:
                    print(f"{name}: Dropped {before - after} rows with invalid operator_id.")
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
                missing_ts = df['timestamp'].isnull().sum()
                if missing_ts > 0:
                    print(f"{name}: Found {missing_ts} invalid timestamp entries, dropping those rows.")
                    df = df.dropna(subset=['timestamp'])
            # Fill missing activity_type with 'Unknown'
            if 'activity_type' in df.columns:
                df['activity_type'] = df['activity_type'].fillna('Unknown')

        return df

    # Load all datasets
    clients = load_csv('clients.csv')
    orders = load_csv('orders.csv')
    operators = load_csv('operators.csv')
    operator_balance = load_csv('operator_balance.csv')
    activity_logs = load_csv('activity_logs.csv')

    # Show overview before repair
    for df, name in zip([clients, orders, operators, operator_balance, activity_logs],
                        ['clients.csv', 'orders.csv', 'operators.csv', 'operator_balance.csv', 'activity_logs.csv']):
        data_overview(df, name)

    # Repair datasets
    clients = repair_df(clients, 'clients.csv')
    orders = repair_df(orders, 'orders.csv')
    operators = repair_df(operators, 'operators.csv')
    operator_balance = repair_df(operator_balance, 'operator_balance.csv')
    activity_logs = repair_df(activity_logs, 'activity_logs.csv')

    # Show overview after repair
    print("\n=== After Repair & Validation ===")
    for df, name in zip([clients, orders, operators, operator_balance, activity_logs],
                        ['clients.csv', 'orders.csv', 'operators.csv', 'operator_balance.csv', 'activity_logs.csv']):
        data_overview(df, name)

    # Return repaired dataframes for further analysis if needed
    return {
        'clients': clients,
        'orders': orders,
        'operators': operators,
        'operator_balance': operator_balance,
        'activity_logs': activity_logs
    }
```