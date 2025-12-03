import duckdb
import os

def generate_report(db_path: str = "sensors.db", output_file: str = "report.csv"):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")

    with open("reports/summary_report.sql", "r") as f:
        query = f.read().strip().rstrip(';')

    con = duckdb.connect(db_path)
    try:
        # Execute query and fetch result
        # We can export directly to CSV using DuckDB's COPY command or just fetch and write.
        # Let's fetch to show it in console too.
        
        result = con.execute(query).fetchall()
        columns = [desc[0] for desc in con.description]
        
        print("Generated Report:")
        print(",".join(columns))
        for row in result:
            print(",".join(map(str, row)))
            
        # Save to CSV
        con.execute(f"COPY ({query}) TO '{output_file}' (HEADER, DELIMITER ',')")
        print(f"\nReport saved to {output_file}")
        
    finally:
        con.close()

if __name__ == "__main__":
    generate_report()
