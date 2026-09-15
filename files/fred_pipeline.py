"""
FRED Data Pipeline
Manages automated data ingestion, storage, and updates
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd
from fred_fetcher import FREDFetcher


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/fred_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FREDPipeline:
    """Manage FRED data ingestion and storage pipeline"""
    
    def __init__(self, config_path: str = 'config.json', api_key: Optional[str] = None):
        """
        Initialize pipeline
        
        Args:
            config_path: Path to configuration file
            api_key: FRED API key
        """
        self.config_path = config_path
        self.fetcher = FREDFetcher(api_key)
        self.config = self._load_config()
        self._setup_directories()
    
    def _setup_directories(self) -> None:
        """Create necessary directories"""
        for directory in ['data', 'logs', 'cache']:
            Path(directory).mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict:
        """Load configuration from JSON file"""
        if Path(self.config_path).exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_config(self) -> None:
        """Save configuration to JSON file"""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def add_series_to_pipeline(
        self,
        series_id: str,
        series_name: str,
        category: str = "general",
        units: str = "lin"
    ) -> None:
        """
        Add a series to the ingestion pipeline
        
        Args:
            series_id: FRED series ID
            series_name: Human-readable name
            category: Category for organization
            units: Unit transformation
        """
        if 'series' not in self.config:
            self.config['series'] = {}
        
        self.config['series'][series_id] = {
            'name': series_name,
            'category': category,
            'units': units,
            'added_date': datetime.now().isoformat()
        }
        
        self._save_config()
        logger.info(f"Added series {series_id} ({series_name}) to pipeline")
    
    def ingest_all_series(self, start_date: Optional[str] = None) -> pd.DataFrame:
        """
        Ingest all configured series
        
        Args:
            start_date: Optional start date (YYYY-MM-DD)
            
        Returns:
            Combined DataFrame with all series
        """
        if not self.config.get('series'):
            logger.warning("No series configured")
            return pd.DataFrame()
        
        series_ids = list(self.config['series'].keys())
        logger.info(f"Ingesting {len(series_ids)} series")
        
        try:
            df = self.fetcher.fetch_multiple_series(series_ids, start_date=start_date)
            
            # Add metadata
            df.attrs['last_updated'] = datetime.now().isoformat()
            df.attrs['num_series'] = len(series_ids)
            
            logger.info(f"Successfully ingested {len(series_ids)} series")
            return df
        
        except Exception as e:
            logger.error(f"Error ingesting series: {e}")
            raise
    
    def update_series(self, series_id: str, start_date: Optional[str] = None) -> pd.DataFrame:
        """
        Update a specific series
        
        Args:
            series_id: FRED series ID
            start_date: Optional start date
            
        Returns:
            Updated DataFrame
        """
        logger.info(f"Updating series {series_id}")
        
        try:
            df = self.fetcher.fetch_series(series_id, start_date=start_date)
            
            # Try to merge with existing data
            cache_file = f'cache/{series_id}_cache.parquet'
            if Path(cache_file).exists():
                existing = pd.read_parquet(cache_file)
                df = pd.concat([existing, df]).drop_duplicates().sort_index()
            
            df.to_parquet(cache_file)
            logger.info(f"Updated {series_id} with {len(df)} observations")
            return df
        
        except Exception as e:
            logger.error(f"Error updating {series_id}: {e}")
            raise
    
    def export_data(
        self,
        df: pd.DataFrame,
        filename: str,
        format: str = 'csv'
    ) -> None:
        """
        Export data to file
        
        Args:
            df: DataFrame to export
            filename: Output filename (without extension)
            format: 'csv' or 'parquet'
        """
        if format == 'csv':
            self.fetcher.save_to_csv(df, f'{filename}.csv')
        elif format == 'parquet':
            self.fetcher.save_to_parquet(df, f'{filename}.parquet')
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_pipeline_status(self) -> Dict:
        """Get status of configured pipeline"""
        series = self.config.get('series', {})
        return {
            'num_series': len(series),
            'series': list(series.keys()),
            'categories': list(set(s.get('category') for s in series.values())),
            'config_file': self.config_path
        }


def setup_example_pipeline() -> FREDPipeline:
    """Create and configure an example pipeline"""
    pipeline = FREDPipeline()
    
    # Add common economic indicators
    economic_series = [
        ('GDP', 'Gross Domestic Product', 'macroeconomic'),
        ('UNRATE', 'Unemployment Rate', 'labor'),
        ('CPIAUCSL', 'Consumer Price Index', 'prices'),
        ('FEDFUNDS', 'Federal Funds Rate', 'interest_rates'),
        ('HOUST', 'Housing Starts', 'real_estate'),
        ('ICSA', 'Initial Claims', 'labor'),
    ]
    
    for series_id, name, category in economic_series:
        pipeline.add_series_to_pipeline(series_id, name, category)
    
    return pipeline


if __name__ == '__main__':
    # Example: Setup and run pipeline
    pipeline = setup_example_pipeline()
    print("\nPipeline Status:")
    print(json.dumps(pipeline.get_pipeline_status(), indent=2))
