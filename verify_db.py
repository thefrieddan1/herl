import duckdb

def verify():
    con = duckdb.connect("sensors.db")
    
    print("Table Schema:")
    print(con.execute("DESCRIBE sensor_readings").fetchall())
    
    print("\nRow Count:")
    print(con.execute("SELECT COUNT(*) FROM sensor_readings").fetchall())
    
    print("\nFirst 5 rows:")
    print(con.execute("SELECT * FROM sensor_readings LIMIT 5").fetchall())
    
    con.close()

if __name__ == "__main__":
    verify()
