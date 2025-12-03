import duckdb
import polars as pl
from typing import Any
from .base import Loader

class DuckDBLoader(Loader):
    def __init__(self, db_path: str, table_name: str):
        self.db_path = db_path
        self.table_name = table_name

    def load(self, data: pl.DataFrame) -> None:
        """
        Loads the Polars DataFrame into a DuckDB table.
        """
        con = duckdb.connect(self.db_path)
        
        try:
            # Convert to Arrow Table
            arrow_table = data.to_arrow()
            
            # Check if table exists, if not create it based on the arrow table schema
            # DuckDB can query Arrow tables directly.
            
            # Create table if not exists
            con.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} AS SELECT * FROM arrow_table LIMIT 0")
            
            # Insert data
            con.execute(f"INSERT INTO {self.table_name} SELECT * FROM arrow_table")
            
        finally:
            con.close()
