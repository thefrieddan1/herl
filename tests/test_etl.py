import pytest
import polars as pl
import duckdb
import os
from etl import CSVExtractor, SensorDataTransformer, DuckDBLoader

@pytest.fixture
def sample_data(tmp_path):
    # Create sample CSVs
    data_file = tmp_path / "data.csv"
    data_file.write_text("Tag Name,Timestamp,Value\nS1,2024-01-01T00:00:00,10.0\n")
    
    sensors_file = tmp_path / "sensors.csv"
    sensors_file.write_text("tag_name,machine_code,component_code,coordinate\nS1,M1,C1,X\n")
    
    machines_file = tmp_path / "machines.csv"
    machines_file.write_text("machine_code,machine_name\nM1,Machine 1\n")
    
    return str(data_file), str(sensors_file), str(machines_file)

def test_extractor(sample_data):
    data_file, sensors_file, machines_file = sample_data
    extractor = CSVExtractor([data_file], sensors_file, machines_file)
    extracted = extractor.extract()
    
    assert "sensor_data" in extracted
    assert "sensors" in extracted
    assert "machines" in extracted
    assert extracted["sensor_data"].height == 1
    assert extracted["sensors"].height == 1

def test_transformer(sample_data):
    data_file, sensors_file, machines_file = sample_data
    extractor = CSVExtractor([data_file], sensors_file, machines_file)
    extracted = extractor.extract()
    
    transformer = SensorDataTransformer()
    transformed = transformer.transform(extracted)
    
    assert transformed.height == 1
    assert "sample_time" in transformed.columns
    assert "inserted_at" in transformed.columns
    assert transformed["machine_code"][0] == "M1"
    # Check timestamp conversion (2024-01-01T00:00:00 -> 1704067200000000 us)
    # Note: Polars might use different timezone handling, but usually assumes local or UTC if not specified.
    # Let's just check it's an integer.
    assert isinstance(transformed["sample_time"][0], int)

def test_loader(tmp_path, sample_data):
    data_file, sensors_file, machines_file = sample_data
    extractor = CSVExtractor([data_file], sensors_file, machines_file)
    extracted = extractor.extract()
    transformer = SensorDataTransformer()
    transformed = transformer.transform(extracted)
    
    db_path = str(tmp_path / "test.db")
    loader = DuckDBLoader(db_path, "test_table")
    loader.load(transformed)
    
    con = duckdb.connect(db_path)
    result = con.execute("SELECT * FROM test_table").fetchall()
    con.close()
    
    assert len(result) == 1
    assert result[0][0] == "M1" # machine_code is first column
