import os
from etl import CSVExtractor, SensorDataTransformer, DuckDBLoader, ETLPipeline

def main():
    # Configuration
    DATA_FILES = ["2024-01-01.csv", "2024-01-02.csv"]
    SENSORS_FILE = "Sensors.csv"
    MACHINES_FILE = "Machines.csv"
    DB_PATH = "sensors.db"
    TABLE_NAME = "sensor_readings"

    # Initialize components
    extractor = CSVExtractor(DATA_FILES, SENSORS_FILE, MACHINES_FILE)
    transformer = SensorDataTransformer()
    loader = DuckDBLoader(DB_PATH, TABLE_NAME)

    # Initialize and run pipeline
    pipeline = ETLPipeline(extractor, transformer, loader)
    pipeline.run()

if __name__ == "__main__":
    main()
