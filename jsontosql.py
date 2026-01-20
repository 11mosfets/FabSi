import json
import pymysql
import sys
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    timeout = 10
    return pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        db=os.getenv("DB_NAME", "defaultdb"),
        host=os.getenv("DB_HOST"),
        password=os.getenv("DB_PASS"),
        read_timeout=timeout,
        port=int(os.getenv("DB_PORT", 23001)),
        user=os.getenv("DB_USER"),
        write_timeout=timeout,
    )

def load_to_sql(json_file):
    """
    Reads the JSON dump and inserts it into the MySQL Database.
    Handles Foreign Key order automatically (Genealogy first).
    """
    print("Connecting to Database...")
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("USE Fab18;")
    except Exception as e:
        print(f" Connection Failed: {e}")
        return

    print(f"Reading {json_file}...")
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File {json_file} not found.")
        return

    load_order = [
        "site_environment_log",
        "lot_genealogy",
        "process_cvd_log",
        "process_litho_log",
        "process_etch_log",
        "metrology_inline",
        "final_yield_log"
    ]

    for table_name in load_order:
        rows = data.get(table_name, [])
        print(f"   Loading {len(rows)} rows into {table_name}...")
        
        if not rows:
            continue

        columns = list(rows[0].keys())
        col_str = ", ".join(columns)
        val_placeholders = ", ".join(["%s"] * len(columns))
        
        query = f"INSERT INTO {table_name} ({col_str}) VALUES ({val_placeholders})"
        
        values = [tuple(row.values()) for row in rows]
        
        try:
            cur.executemany(query, values)
            conn.commit()
        except Exception as e:
            print(f"   Error loading {table_name}: {e}")
            conn.rollback()

    print("Data Load Complete!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        target_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
        # target_file = f"jsons/fab_data_{target_date}.json"
        target_file = "jsons/fab_full_dump.json"
    
    load_to_sql(target_file)