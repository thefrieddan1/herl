from fastapi import FastAPI, File, UploadFile, HTTPException
from typing import List
import tempfile
import os
import shutil
import duckdb
from pathlib import Path

from etl import CSVExtractor, SensorDataTransformer, DuckDBLoader, ETLPipeline

app = FastAPI(title="Sensor Data Report API", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "Sensor Data Report API. Use POST /report to generate reports."}

@app.post("/report")
async def generate_report(
    sensor_files: List[UploadFile] = File(..., description="Sensor sample CSV files"),
    sensors_metadata: UploadFile = File(..., description="Sensors.csv metadata file"),
    machines_metadata: UploadFile = File(..., description="Machines.csv metadata file")
):
    """
    Accepts sensor sample CSV files and metadata files, runs ETL, and returns a summary report.
    
    Returns:
        JSON array with the report data containing:
        - machine_name: User-friendly machine name
        - coordinate: Coordinate with the highest increase
        - value_avg: Average value of the day
        - increase_in_value: Increase from previous day
        - samples_cnt: Number of records for this coordinate
    """
    
    # Create a temporary directory for this request
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create data subdirectory in temp directory
        data_dir = os.path.join(temp_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        
        # Save uploaded files to temp directory
        sensor_file_paths = []
        for sensor_file in sensor_files:
            file_path = os.path.join(temp_dir, sensor_file.filename)
            with open(file_path, "wb") as f:
                content = await sensor_file.read()
                f.write(content)
            sensor_file_paths.append(file_path)
        
        sensors_file_path = os.path.join(temp_dir, "data/Sensors.csv")
        with open(sensors_file_path, "wb") as f:
            content = await sensors_metadata.read()
            f.write(content)
        
        machines_file_path = os.path.join(temp_dir, "data/Machines.csv")
        with open(machines_file_path, "wb") as f:
            content = await machines_metadata.read()
            f.write(content)
        
        # Create a temporary database
        db_path = os.path.join(temp_dir, "temp_sensors.db")
        
        # Run ETL Pipeline
        extractor = CSVExtractor(sensor_file_paths, sensors_file_path, machines_file_path)
        transformer = SensorDataTransformer()
        loader = DuckDBLoader(db_path, "sensor_readings")
        
        pipeline = ETLPipeline(extractor, transformer, loader)
        pipeline.run()
        
        # Generate report
        # Read SQL query
        with open("reports/summary_report.sql", "r") as f:
            query = f.read().strip().rstrip(';')
        
        # Execute query
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            con = duckdb.connect(db_path)
            result = con.execute(query).fetchall()
            columns = [desc[0] for desc in con.description]
            con.close()
        finally:
            os.chdir(original_dir)
        
        # Convert to JSON format
        report = []
        for row in result:
            report.append(dict(zip(columns, row)))
        
        return report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing files: {str(e)}")
    
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
