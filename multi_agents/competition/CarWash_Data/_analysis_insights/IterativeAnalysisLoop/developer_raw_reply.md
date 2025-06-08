```python
import os
import pandas as pd
from datetime import datetime

def analyze_and_flag_future_dates(data_directory_path):
    # Filenames to check for future-dated timestamps
    # Assuming bookings and transactions tables have timestamps to check
    filenames = {
        'bookings': 'bookings.csv',
        'transactions': 'transactions.csv'
    }
    
    # Columns suspected to hold timestamps - these might vary by dataset; 
    # we will try common timestamp columns, else print a warning.
    timestamp_columns_candidates = {
        'bookings': ['booking_datetime', 'booking_date', 'created_at', 'timestamp'],
        'transactions': ['transaction_datetime', 'transaction_date', 'created_at', 'timestamp']
    }
    
    now = pd.Timestamp.now()
    
    for table_name, filename in filenames.items():
        file_path = os.path.join(data_directory_path, filename)
        print(f"\nProcessing table '{table_name}' from file: {filename}")
        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"  ERROR: File not found: {file_path}")
            continue
        except Exception as e:
            print(f"  ERROR: Failed to load {filename}: {e}")
            continue
        
        # Identify timestamp columns present in the dataframe
        available_ts_cols = [col for col in timestamp_columns_candidates[table_name] if col in df.columns]
        if not available_ts_cols:
            print("  WARNING: No recognized timestamp columns found in this dataset.")
            continue
        
        for ts_col in available_ts_cols:
            # Attempt to parse column to datetime, coerce errors to NaT
            df[ts_col + '_parsed'] = pd.to_datetime(df[ts_col], errors='coerce', utc=True)
            
            # Count how many could not be parsed
            unparsable_count = df[ts_col + '_parsed'].isna().sum()
            total_count = len(df)
            
            print(f"  Timestamp column '{ts_col}':")
            print(f"    Total records: {total_count}")
            print(f"    Unparsable date entries: {unparsable_count} ({unparsable_count / total_count * 100:.2f}%)")
            
            # Identify future dates relative to now (considering UTC)
            future_mask = df[ts_col + '_parsed'] > now
            future_count = future_mask.sum()
            if future_count > 0:
                print(f"    Future-dated timestamps found: {future_count} ({future_count / total_count * 100:.2f}%)")
                
                # Show earliest and latest future timestamps for context
                future_dates = df.loc[future_mask, ts_col + '_parsed']
                earliest_future = future_dates.min()
                latest_future = future_dates.max()
                print(f"      Earliest future date: {earliest_future}")
                print(f"      Latest future date: {latest_future}")
                
                # Flag these rows by adding a boolean column
                flag_column = ts_col + '_is_future'
                df[flag_column] = future_mask
                
                # Optionally: output summary counts of flagged rows by another grouping column if exists
                # For example, grouping by a user_id or booking_id if present
                grouping_cols = ['user_id', 'booking_id', 'transaction_id']
                grouping_col = next((c for c in grouping_cols if c in df.columns), None)
                if grouping_col:
                    flagged_counts = df.loc[future_mask].groupby(grouping_col).size().sort_values(ascending=False).head(5)
                    print(f"      Top 5 {grouping_col}s with future timestamps and their counts:")
                    for idx, cnt in flagged_counts.items():
                        print(f"        {grouping_col}={idx}: {cnt}")
                
                # Save flagged data or summary could be implemented here if needed
                
            else:
                print(f"    No future-dated timestamps found in this column.")
            
            # Drop the parsed column to clean up df (unless needed later)
            df.drop(columns=[ts_col + '_parsed'], inplace=True)
```