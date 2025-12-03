import pytest
from fastapi.testclient import TestClient
from api.main import app
import io

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_generate_report():
    # Create sample CSV files in memory
    sensor_data_1 = """Tag Name,Timestamp,Value
S1,2024-01-01T00:00:00,10.0
S2,2024-01-01T00:00:00,15.0
"""
    
    sensor_data_2 = """Tag Name,Timestamp,Value
S1,2024-01-02T00:00:00,20.0
S2,2024-01-02T00:00:00,18.0
"""
    
    sensors_metadata = """tag_name,machine_code,component_code,coordinate
S1,M1,Component1,X
S2,M1,Component2,Y
"""
    
    machines_metadata = """machine_code,machine_name
M1,Machine One
"""
    
    # Prepare files for upload
    # For multiple files with the same parameter name, we need to use a list of tuples
    files = [
        ("sensor_files", ("2024-01-01.csv", io.BytesIO(sensor_data_1.encode()), "text/csv")),
        ("sensor_files", ("2024-01-02.csv", io.BytesIO(sensor_data_2.encode()), "text/csv")),
        ("sensors_metadata", ("Sensors.csv", io.BytesIO(sensors_metadata.encode()), "text/csv")),
        ("machines_metadata", ("Machines.csv", io.BytesIO(machines_metadata.encode()), "text/csv"))
    ]
    
    response = client.post("/report", files=files)
    
    assert response.status_code == 200
    data = response.json()
    
    # Should have 1 result (1 machine)
    assert isinstance(data, list)
    assert len(data) == 1
    
    # Check structure
    result = data[0]
    assert "machine_name" in result
    assert "coordinate" in result
    assert "value_avg" in result
    assert "increase_in_value" in result
    assert "samples_cnt" in result
    
    # Check values
    assert result["machine_name"] == "Machine One"
    # Coordinate X has increase of 10 (10->20), Y has increase of 3 (15->18)
    assert result["coordinate"] == "X"
    assert result["value_avg"] == 20.0
    assert result["increase_in_value"] == 10.0
