import pytest
import duckdb
import os
import shutil

def test_summary_report(tmp_path):
    # Setup
    db_path = tmp_path / "test_sensors.db"
    con = duckdb.connect(str(db_path))
    
    # Create sensor_readings table
    con.execute("""
        CREATE TABLE sensor_readings (
            machine_code VARCHAR,
            component_code VARCHAR,
            coordinate VARCHAR,
            sample_time BIGINT,
            value DOUBLE,
            inserted_at TIMESTAMP
        )
    """)
    
    # Insert test data
    # Machine M1:
    # Coord C1: 2024-01-01 Avg = 10, 2024-01-02 Avg = 20 -> Increase = 10
    # Coord C2: 2024-01-01 Avg = 10, 2024-01-02 Avg = 15 -> Increase = 5
    # Expected: M1 -> C1
    
    # Machine M2:
    # Coord C3: 2024-01-01 Avg = 10, 2024-01-02 Avg = 5 -> Increase = -5 (Decrease)
    # Coord C4: 2024-01-01 Avg = 10, 2024-01-02 Avg = 30 -> Increase = 20
    # Expected: M2 -> C4
    
    # Timestamps:
    # 2024-01-01 00:00:00 -> 1704067200000000
    # 2024-01-02 00:00:00 -> 1704153600000000
    
    con.execute("INSERT INTO sensor_readings VALUES ('M1', 'Comp', 'C1', 1704067200000000, 10.0, now())")
    con.execute("INSERT INTO sensor_readings VALUES ('M1', 'Comp', 'C1', 1704153600000000, 20.0, now())")
    
    con.execute("INSERT INTO sensor_readings VALUES ('M1', 'Comp', 'C2', 1704067200000000, 10.0, now())")
    con.execute("INSERT INTO sensor_readings VALUES ('M1', 'Comp', 'C2', 1704153600000000, 15.0, now())")
    
    con.execute("INSERT INTO sensor_readings VALUES ('M2', 'Comp', 'C3', 1704067200000000, 10.0, now())")
    con.execute("INSERT INTO sensor_readings VALUES ('M2', 'Comp', 'C3', 1704153600000000, 5.0, now())")
    
    con.execute("INSERT INTO sensor_readings VALUES ('M2', 'Comp', 'C4', 1704067200000000, 10.0, now())")
    con.execute("INSERT INTO sensor_readings VALUES ('M2', 'Comp', 'C4', 1704153600000000, 30.0, now())")
    
    con.close()
    
    # Create data subdirectory and Machines.csv in it
    data_dir = tmp_path / "data"
    data_dir.mkdir(exist_ok=True)
    machines_csv = data_dir / "Machines.csv"
    machines_csv.write_text("machine_code,machine_name\nM1,Machine One\nM2,Machine Two\n")
    
    # Read SQL query
    # Assuming tests are run from project root
    with open("reports/summary_report.sql", "r") as f:
        query = f.read()
        
    # Execute query using the temp db and temp Machines.csv
    # We need to change CWD to tmp_path so DuckDB finds Machines.csv
    
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        con = duckdb.connect(str(db_path))
        result = con.execute(query).fetchall()
        con.close()
    finally:
        os.chdir(cwd)
        
    # Verify results
    # Expected:
    # Machine Two, C4, 30.0, 20.0, 1
    # Machine One, C1, 20.0, 10.0, 1
    
    # Sort by increase desc
    assert len(result) == 2
    
    row1 = result[0]
    assert row1[0] == "Machine Two"
    assert row1[1] == "C4"
    assert row1[3] == 20.0
    
    row2 = result[1]
    assert row2[0] == "Machine One"
    assert row2[1] == "C1"
    assert row2[3] == 10.0
