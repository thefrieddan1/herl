# Sensor Data ETL and Report API

This project implements an ETL infrastructure for sensor data with SQL-based reporting and a REST API.

## Project Structure

```
.
├── etl/                    # ETL pipeline components
│   ├── base.py            # Abstract base classes
│   ├── extractors.py      # CSV data extraction
│   ├── transformers.py    # Data transformation
│   ├── loaders.py         # DuckDB loading
│   └── pipeline.py        # ETL orchestration
├── api/                    # FastAPI application
│   └── main.py            # REST API endpoints
├── reports/                # SQL reports
│   └── summary_report.sql # Summary report query
├── tests/                  # Unit and integration tests
│   ├── test_etl.py        # ETL tests
│   ├── test_report.py     # Report tests
│   └── test_api.py        # API tests
├── main.py                 # ETL entry point
├── generate_report.py      # Report generation script
└── verify_db.py           # Database verification script
```

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Part 1: ETL Pipeline

Run the ETL to load sensor data into DuckDB:

```bash
python main.py
```

This creates `sensors.db` with the `sensor_readings` table.

**Storage Target**: DuckDB database file (`sensors.db`)

**Table Schema**:
```sql
CREATE TABLE sensor_readings (
    machine_code VARCHAR,
    component_code VARCHAR,
    coordinate VARCHAR,
    sample_time BIGINT,      -- Epoch microseconds
    value DOUBLE,
    inserted_at TIMESTAMP
);
```

### Part 2: Generate Report

Generate the summary report:

```bash
python generate_report.py
```

This outputs the report to console and saves it to `report.csv`.

### Part 3: API Endpoint

Start the API server:

```bash
uvicorn api.main:app --reload
```

Test the API:

```bash
curl -X POST "http://localhost:8000/report" \
  -F "sensor_files=@2024-01-01.csv" \
  -F "sensor_files=@2024-01-02.csv" \
  -F "sensors_metadata=@Sensors.csv" \
  -F "machines_metadata=@Machines.csv"
```

API Documentation: http://localhost:8000/docs

## Testing

Run all tests:

```bash
pytest
```

Run specific test suites:

```bash
pytest tests/test_etl.py      # ETL tests
pytest tests/test_report.py   # Report tests
pytest tests/test_api.py      # API tests
```

## Design & Extensibility

### Abstract Base Classes

The ETL pipeline uses abstract base classes (`Extractor`, `Transformer`, `Loader`) to enable easy swapping of:
- **Data sources**: CSV → JSON, Parquet, API, etc.
- **Processing engines**: Polars → Pandas, DuckDB, Spark, etc.
- **Storage targets**: DuckDB → PostgreSQL, MySQL, Parquet, etc.

### Technology Stack

- **Polars**: Fast, memory-efficient data processing
- **DuckDB**: Embedded analytical database
- **FastAPI**: Modern, high-performance API framework
- **PyArrow**: Zero-copy data transfer between Polars and DuckDB

## Report Output

The summary report includes:
- `machine_name`: User-friendly machine name
- `coordinate`: Coordinate with the highest increase
- `value_avg`: Average value on 2024-01-02
- `increase_in_value`: Increase from 2024-01-01 to 2024-01-02
- `samples_cnt`: Number of samples

## License

Internal project for Razor Labs.
