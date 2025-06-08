```python
import os
import pandas as pd
import numpy as np

def analyze_service_packages_and_extras(data_directory_path):
    try:
        # Load main data file - assuming a relevant file name for service package and extra services
        file_path = os.path.join(data_directory_path, 'car_wash_transactions.csv')
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"ERROR: File not found at path: {file_path}")
        return
    except Exception as e:
        print(f"ERROR: Unable to load data due to: {e}")
        return

    # Check columns to understand data structure
    print("Columns in dataset:", df.columns.tolist())

    # Assuming columns like 'ServicePackage', 'ExtraServices', 'TransactionDate', 'Price', 'CustomerID' exist
    # Adjust column names if necessary based on actual data

    # Basic data info
    print(f"\nTotal transactions loaded: {len(df)}")

    # Clean data: drop rows with missing critical info in ServicePackage or Price
    df_clean = df.dropna(subset=['ServicePackage', 'Price'])
    dropped = len(df) - len(df_clean)
    if dropped > 0:
        print(f"Dropped {dropped} transactions due to missing ServicePackage or Price")

    # Summary statistics on Price by ServicePackage
    print("\n--- Price Summary Statistics by Service Package ---")
    package_stats = df_clean.groupby('ServicePackage')['Price'].agg(['count', 'mean', 'median', 'min', 'max',
                                                                    lambda x: np.percentile(x, 25),
                                                                    lambda x: np.percentile(x, 75)])
    package_stats.columns = ['Count', 'Mean Price', 'Median Price', 'Min Price', 'Max Price', '25th Percentile', '75th Percentile']
    print(package_stats.sort_values('Count', ascending=False).to_string(float_format='${:,.2f}'.format))

    # Distribution of Service Packages (percentage of total transactions)
    total_tx = len(df_clean)
    service_dist = df_clean['ServicePackage'].value_counts(normalize=True).mul(100).round(2)
    print("\n--- Service Package Distribution (Percentage of Transactions) ---")
    for pkg, pct in service_dist.items():
        print(f"{pkg}: {pct:.2f}%")

    # Analyze Extra Services
    # Assume 'ExtraServices' is a string column with comma-separated extras or NaN if none
    df_clean['ExtraServices'] = df_clean['ExtraServices'].fillna('')
    # Extract all extra services into a list and explode
    df_clean['ExtraServicesList'] = df_clean['ExtraServices'].apply(lambda x: [e.strip() for e in x.split(',') if e.strip()] if x else [])
    extras_series = df_clean.explode('ExtraServicesList')['ExtraServicesList']

    # Count and percentage of transactions with extras
    with_extras = df_clean[df_clean['ExtraServicesList'].map(len) > 0]
    pct_with_extras = len(with_extras) / total_tx * 100
    print(f"\nPercentage of transactions with at least one extra service: {pct_with_extras:.2f}%")

    # Top 10 most popular extra services with counts and percentages
    extras_counts = extras_series.value_counts()
    extras_pct = (extras_counts / total_tx * 100).round(2)
    print("\n--- Top 10 Extra Services by Count and Percentage of All Transactions ---")
    top_n = 10
    for extra, count in extras_counts.head(top_n).items():
        pct = extras_pct.loc[extra]
        print(f"{extra}: {count} transactions, {pct:.2f}% of all transactions")

    # Average price difference for transactions with extras vs without extras
    avg_price_with_extras = with_extras['Price'].mean()
    avg_price_without_extras = df_clean[df_clean['ExtraServicesList'].map(len) == 0]['Price'].mean()
    print(f"\nAverage Price with Extras: ${avg_price_with_extras:.2f}")
    print(f"Average Price without Extras: ${avg_price_without_extras:.2f}")
    price_diff = avg_price_with_extras - avg_price_without_extras
    print(f"Average price increase due to extras: ${price_diff:.2f}")

    # Growth/Change over time analysis on service package usage
    # Assuming 'TransactionDate' is available and parseable
    try:
        df_clean['TransactionDate'] = pd.to_datetime(df_clean['TransactionDate'])
    except Exception:
        print("\nWARNING: Could not parse 'TransactionDate' column for time-based analysis.")
        return

    df_clean['YearMonth'] = df_clean['TransactionDate'].dt.to_period('M')
    monthly_counts = df_clean.groupby(['YearMonth', 'ServicePackage']).size().unstack(fill_value=0)

    # Calculate month-over-month percentage growth for top 3 packages by total counts
    top_packages = monthly_counts.sum().sort_values(ascending=False).head(3).index.tolist()
    print("\n--- Month-over-Month Growth Rates for Top 3 Service Packages ---")
    for pkg in top_packages:
        counts = monthly_counts[pkg]
        growth = counts.pct_change().replace([np.inf, -np.inf], np.nan).fillna(0) * 100
        avg_growth = growth.mean()
        print(f"{pkg}: Average MoM Growth = {avg_growth:.2f}%")
        # Print last 3 months growth for recent insight
        print(f"Last 3 months MoM growth for {pkg}:")
        for date, g in growth[-3:].items():
            print(f"  {date}: {g:.2f}%")

    # Correlation between number of extra services and price
    df_clean['NumExtras'] = df_clean['ExtraServicesList'].apply(len)
    corr = df_clean[['NumExtras', 'Price']].corr().loc['NumExtras', 'Price']
    print(f"\nCorrelation between number of extras and price: {corr:.3f}")

```