"""
FRED Data Fetcher
Fetches economic data from the Federal Reserve Economic Data (FRED) API
"""

import os
import pandas as pd
import requests
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class FREDFetcher:
    """Fetch and manage FRED economic data"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FRED fetcher
        
        Args:
            api_key: FRED API key. If None, will look for FRED_API_KEY env var
        """
        self.api_key = api_key or os.getenv('API Key')
        if not self.api_key:
            raise ValueError(
                "FRED API key not provided. Set FRED_API_KEY environment variable "
                "or pass api_key parameter. Get key at: https://fredaccount.stlouisfed.org/login"
            )
        self.base_url = "https://api.stlouisfed.org/fred"
        self.data_cache = {}
    
    def fetch_series(
        self, 
        series_id: str, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        units: str = "lin"
    ) -> pd.DataFrame:
        """
        Fetch a single FRED data series
        
        Args:
            series_id: FRED series ID (e.g., 'GDP', 'UNRATE')
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            units: Unit transformation - 'lin' (levels), 'chg' (change), 'ch1' (change from year ago)
            
        Returns:
            DataFrame with date index and values
        """
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json',
            'units': units
        }
        
        if start_date:
            params['observation_start'] = start_date
        if end_date:
            params['observation_end'] = end_date
        
        response = requests.get(f"{self.base_url}/series/observations", params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'observations' not in data or not data['observations']:
            raise ValueError(f"No data found for series: {series_id}")
        
        # Convert to DataFrame
        observations = data['observations']
        df = pd.DataFrame(observations)
        df['date'] = pd.to_datetime(df['date'])
        df['value'] = pd.to_numeric(df['value'], errors='coerce')
        df = df.set_index('date')
        
        # Cache the data
        self.data_cache[series_id] = df
        
        return df[['value']].rename(columns={'value': series_id})
    
    def fetch_multiple_series(
        self,
        series_ids: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        units: str = "lin"
    ) -> pd.DataFrame:
        """
        Fetch multiple FRED data series and combine into single DataFrame
        
        Args:
            series_ids: List of FRED series IDs
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            units: Unit transformation
            
        Returns:
            Combined DataFrame with all series
        """
        dfs = []
        for series_id in series_ids:
            try:
                df = self.fetch_series(series_id, start_date, end_date, units)
                dfs.append(df)
                print(f"✓ Fetched {series_id}")
            except Exception as e:
                print(f"✗ Error fetching {series_id}: {e}")
        
        if not dfs:
            raise ValueError("No series were successfully fetched")
        
        # Combine all series
        combined = pd.concat(dfs, axis=1)
        return combined
    
    def get_series_info(self, series_id: str) -> Dict:
        """
        Get metadata about a FRED series
        
        Args:
            series_id: FRED series ID
            
        Returns:
            Dictionary with series information
        """
        params = {
            'series_id': series_id,
            'api_key': self.api_key,
            'file_type': 'json'
        }
        
        response = requests.get(f"{self.base_url}/series", params=params)
        response.raise_for_status()
        
        data = response.json()
        return data['seriess'][0] if data.get('seriess') else {}
    
    def save_to_csv(self, df: pd.DataFrame, filename: str) -> None:
        """Save fetched data to CSV"""
        Path('data').mkdir(exist_ok=True)
        filepath = f'data/{filename}'
        df.to_csv(filepath)
        print(f"✓ Saved data to {filepath}")
    
    def save_to_parquet(self, df: pd.DataFrame, filename: str) -> None:
        """Save fetched data to Parquet (efficient format)"""
        Path('data').mkdir(exist_ok=True)
        filepath = f'data/{filename}'
        df.to_parquet(filepath)
        print(f"✓ Saved data to {filepath}")
