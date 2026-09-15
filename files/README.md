# FRED Data Ingestion Pipeline

A Python-based pipeline for fetching and managing Federal Reserve Economic Data (FRED) for analysis.

## Quick Start

### 1. Get Your FRED API Key

1. Visit https://fredaccount.stlouisfed.org/login
2. Sign up for a free account
3. In your account, find your API key
4. Copy your API key

### 2. Setup Project

```bash
# Clone or download this project
cd fred-data-ingestion

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and paste your FRED_API_KEY
```

### 3. Run Examples

```bash
# Try the basic example
python example_usage.py
```

## Project Structure

```
fred-data-ingestion/
├── fred_fetcher.py      # Core FRED API fetcher
├── fred_pipeline.py     # Data pipeline and orchestration
├── example_usage.py     # Example usage patterns
├── requirements.txt     # Python dependencies
├── .env.example         # Environment template
├── config.json          # Pipeline configuration (auto-created)
├── data/                # Output data files
├── cache/               # Cached FRED data
└── logs/                # Pipeline logs
```

## Usage

### Basic Usage: Fetch Single Series

```python
from fred_fetcher import FREDFetcher

# Initialize
fetcher = FREDFetcher()

# Fetch unemployment data
unrate = fetcher.fetch_series(
    'UNRATE',
    start_date='2020-01-01',
    end_date='2024-01-01'
)

print(unrate.head())
```

### Fetch Multiple Series

```python
# Fetch multiple economic indicators
series_list = ['GDP', 'UNRATE', 'CPIAUCSL']

economic_data = fetcher.fetch_multiple_series(
    series_list,
    start_date='2022-01-01'
)

# Save to file
fetcher.save_to_csv(economic_data, 'economic_data.csv')
fetcher.save_to_parquet(economic_data, 'economic_data.parquet')
```

### Use Pipeline for Automated Ingestion

```python
from fred_pipeline import FREDPipeline

# Create pipeline
pipeline = FREDPipeline()

# Add series to monitor
pipeline.add_series_to_pipeline('GDP', 'Gross Domestic Product', 'macroeconomic')
pipeline.add_series_to_pipeline('UNRATE', 'Unemployment Rate', 'labor')
pipeline.add_series_to_pipeline('CPIAUCSL', 'Consumer Price Index', 'prices')

# Ingest all series
data = pipeline.ingest_all_series(start_date='2020-01-01')

# Export data
pipeline.export_data(data, 'economic_indicators', format='csv')

# Check pipeline status
print(pipeline.get_pipeline_status())
```

## Common FRED Series IDs

### Macroeconomic
- `GDP` - Gross Domestic Product
- `GDPC1` - Real GDP
- `GPPIYG` - GDP Price Index

### Employment & Labor
- `UNRATE` - Unemployment Rate
- `PAYEMS` - Total Nonfarm Payroll
- `ICSA` - Initial Claims

### Prices & Inflation
- `CPIAUCSL` - Consumer Price Index (All-Urban)
- `PCEPI` - Personal Consumption Expenditures Price Index
- `CPILFESL` - Core CPI (excluding food and energy)

### Interest Rates
- `FEDFUNDS` - Effective Federal Funds Rate
- `DGS10` - 10-Year Treasury Yield
- `MORTGAGE30US` - 30-Year Mortgage Rate

### Real Estate
- `HOUST` - Housing Starts
- `MMNRNJ` - Median Home Price
- `MORTGAGE` - Mortgage Rate

[See full series list](https://fred.stlouisfed.org/)

## Data Analysis Examples

### Calculate Year-over-Year Change

```python
data = fetcher.fetch_series('CPIAUCSL', start_date='2020-01-01')
data['YoY_Change'] = data['CPIAUCSL'].pct_change(periods=12) * 100
print(f"Current inflation: {data['YoY_Change'].iloc[-1]:.2f}%")
```

### Combine Multiple Series Analysis

```python
data = fetcher.fetch_multiple_series(['UNRATE', 'PAYEMS'], start_date='2020-01-01')

# Drop NaN values
data_clean = data.dropna()

# Calculate correlations
correlation = data_clean.corr()
print(correlation)
```

### Export for Further Analysis

```python
# Export to parquet (more efficient than CSV)
fetcher.save_to_parquet(data, 'fred_data.parquet')

# Load later for analysis
loaded_data = pd.read_parquet('data/fred_data.parquet')
```

## Environment Variables

Create a `.env` file in the project root:

```
FRED_API_KEY=your_api_key_here
DATABASE_URL=sqlite:///fred_data.db  # Optional: for future database storage
```

The `.env.example` file shows all available options.

## Error Handling

The fetcher includes error handling for common issues:

```python
try:
    data = fetcher.fetch_series('INVALID_ID')
except ValueError as e:
    print(f"Series not found: {e}")
except requests.HTTPError as e:
    print(f"API error: {e}")
```

## Next Steps

1. **Database Storage**: Integrate with SQLAlchemy for persistent storage
2. **Scheduling**: Add APScheduler for automatic daily/weekly updates
3. **API Wrapper**: Build a REST API around the pipeline
4. **Dashboard**: Create visualization dashboards with Plotly/Streamlit
5. **Caching**: Implement smart caching to reduce API calls
6. **Data Validation**: Add data quality checks and anomaly detection

## Troubleshooting

### "FRED API key not provided"
- Check that `.env` file exists
- Verify `FRED_API_KEY` is in `.env`
- Ensure `.env` is in the project root

### "No data found for series"
- Verify the series ID is correct
- Check FRED website for series availability
- Try with different date ranges

### Rate Limiting
- FRED API allows ~120 requests per minute
- Implement delays between requests if needed:
  ```python
  import time
  time.sleep(1)  # Wait 1 second between requests
  ```

## Resources

- [FRED API Documentation](https://fred.stlouisfed.org/docs/api/fred/)
- [FRED Series Search](https://fred.stlouisfed.org/)
- [API Key Registration](https://fredaccount.stlouisfed.org/login)
- [pandas-datareader Documentation](https://pandas-datareader.readthedocs.io/)

## License

This project is open source. Use it freely for your economic data analysis.
