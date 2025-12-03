from typing import Dict, Any
import polars as pl
from datetime import datetime
from .base import Transformer

class SensorDataTransformer(Transformer):
    def transform(self, data: Dict[str, pl.DataFrame]) -> pl.DataFrame:
        """
        Transforms the extracted data into the target schema.
        """
        sensor_data = data["sensor_data"]
        sensors = data["sensors"]
        
        # Join sensor data with sensors metadata
        # sensor_data: Tag Name, Timestamp, Value
        # sensors: tag_name, machine_code, component_code, coordinate
        
        joined_df = sensor_data.join(
            sensors, 
            left_on="Tag Name", 
            right_on="tag_name", 
            how="left"
        )
        
        # Convert Timestamp to epoch microseconds
        # Assuming Timestamp is in ISO 8601 format like '2024-01-01T00:00:00'
        
        # We need to parse the string to datetime first, then to epoch microseconds
        # Polars str.to_datetime() usually works well.
        
        transformed_df = joined_df.with_columns([
            pl.col("Timestamp").str.to_datetime().dt.epoch(time_unit="us").alias("sample_time"),
            pl.lit(datetime.now()).alias("inserted_at"),
            pl.col("Value").alias("value")
        ])
        
        # Select and reorder columns as per requirements:
        # machine_code, component_code, coordinate, sample_time, value, inserted_at
        
        final_df = transformed_df.select([
            "machine_code",
            "component_code",
            "coordinate",
            "sample_time",
            "value",
            "inserted_at"
        ])
        
        return final_df
