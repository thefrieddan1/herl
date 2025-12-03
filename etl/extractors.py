from typing import List, Dict, Any
import polars as pl
from .base import Extractor
import os

class CSVExtractor(Extractor):
    def __init__(self, data_files: List[str], sensors_file: str, machines_file: str):
        self.data_files = data_files
        self.sensors_file = sensors_file
        self.machines_file = machines_file

    def extract(self) -> Dict[str, Any]:
        """
        Reads the CSV files and returns a dictionary of Polars DataFrames.
        """
        data_dfs = []
        for file_path in self.data_files:
            if os.path.exists(file_path):
                # Read CSV, assuming standard format. 
                # We might need to handle specific parsing options if needed, 
                # but Polars is usually good at auto-detecting.
                df = pl.read_csv(file_path, null_values=["ERR", "NA"])
                data_dfs.append(df)
            else:
                raise FileNotFoundError(f"Data file not found: {file_path}")
        
        # Concatenate all data files into one DataFrame
        if data_dfs:
            combined_data_df = pl.concat(data_dfs)
        else:
            combined_data_df = pl.DataFrame()

        if os.path.exists(self.sensors_file):
            sensors_df = pl.read_csv(self.sensors_file)
        else:
             raise FileNotFoundError(f"Sensors file not found: {self.sensors_file}")

        if os.path.exists(self.machines_file):
            machines_df = pl.read_csv(self.machines_file)
        else:
             raise FileNotFoundError(f"Machines file not found: {self.machines_file}")
            
        return {
            "sensor_data": combined_data_df,
            "sensors": sensors_df,
            "machines": machines_df
        }
