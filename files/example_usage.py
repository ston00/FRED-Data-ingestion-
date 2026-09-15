"""
Example usage of FRED Data Fetcher
Shows how to fetch and work with FRED data
"""

from fred_fetcher import FREDFetcher
from datetime import datetime, timedelta


def main():
    # Initialize fetcher (requires FRED_API_KEY environment variable)
    fetcher = FREDFetcher()
    
    # Example 1: Fetch single series - Unemployment Rate
    print("=" * 60)
    print("Example 1: Fetching Single Series")
    print("=" * 60)
    
    try:
        unrate = fetcher.fetch_series(
            'UNRATE',  # Unemployment Rate
            start_date='2020-01-01',
            end_date='2024-01-01'
        )
        print(f"\nUnemployment Rate (2020-2024):\n{unrate.head()}")
        print(f"Latest value: {unrate.iloc[-1].values[0]:.2f}%")
        
        # Get series metadata
        info = fetcher.get_series_info('UNRATE')
        print(f"\nSeries Title: {info.get('title')}")
        print(f"Description: {info.get('notes')}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Fetch multiple related series
    print("\n" + "=" * 60)
    print("Example 2: Fetching Multiple Series")
    print("=" * 60)
    
    series_list = [
        'GDP',      # Gross Domestic Product
        'UNRATE',   # Unemployment Rate
        'CPIAUCSL'  # Consumer Price Index
    ]
    
    try:
        economic_data = fetcher.fetch_multiple_series(
            series_list,
            start_date='2022-01-01',
            end_date='2024-01-01'
        )
        
        print(f"\nCombined Economic Data:\n{economic_data.head()}")
        print(f"\nShape: {economic_data.shape}")
        print(f"\nMissing values:\n{economic_data.isnull().sum()}")
        
        # Save results
        fetcher.save_to_csv(economic_data, 'economic_data.csv')
        fetcher.save_to_parquet(economic_data, 'economic_data.parquet')
    
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Analysis example
    print("\n" + "=" * 60)
    print("Example 3: Basic Analysis")
    print("=" * 60)
    
    try:
        # Fetch inflation data
        cpi = fetcher.fetch_series(
            'CPIAUCSL',
            start_date='2020-01-01'
        )
        
        # Calculate month-over-month and year-over-year changes
        cpi['MoM_Change'] = cpi['CPIAUCSL'].pct_change() * 100
        cpi['YoY_Change'] = cpi['CPIAUCSL'].pct_change(periods=12) * 100
        
        print(f"\nCPI Analysis (2020-present):\n{cpi.tail(10)}")
        print(f"\nCurrent YoY Inflation: {cpi['YoY_Change'].iloc[-1]:.2f}%")
    
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
