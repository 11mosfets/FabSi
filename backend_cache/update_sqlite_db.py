import os
import pymysql
import pandas as pd
import sqlite3
from dotenv import load_dotenv, find_dotenv

# Let dotenv find the file automatically by walking up the directory tree
env_path = find_dotenv()
load_status = load_dotenv(env_path, override=True)

print(f"DEBUG: find_dotenv() found: '{env_path}'")
print(f"DEBUG: load_dotenv() returned: {load_status}")

def get_db_connection():
    timeout = 100
    host = os.getenv("MYSQL_HOST") or os.getenv("DB_HOST")
    if not host:
        print(f"CRITICAL ERROR: MYSQL_HOST (or DB_HOST) is empty! load_dotenv tried to read: {env_path}")
        print(f"Check if the file exists and has MYSQL_HOST or DB_HOST defined.")
        raise ValueError("Missing database credentials")
        
    return pymysql.connect(
        charset="utf8mb4",
        connect_timeout=timeout,
        cursorclass=pymysql.cursors.DictCursor,
        database=os.getenv("MYSQL_DB") or os.getenv("DB_NAME", "defaultdb"),
        host=host,
        password=os.getenv("MYSQL_PASSWORD") or os.getenv("DB_PASS"),
        read_timeout=timeout,
        port=int(os.getenv("MYSQL_PORT") or os.getenv("DB_PORT", 23001)),
        user=os.getenv("MYSQL_USER") or os.getenv("DB_USER"),
        write_timeout=timeout,
    )

def update_cache():
    print("Connecting to MySQL...")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("USE Fab18;")
            query = """
            SELECT 
                g.lot_id, 
                g.end_time as timestamp,
                y.yield_percentage,
                c.actual_temp as cvd_temp,
                c.recipe_target_temp as target_temp,
                l.focus_offset as litho_focus,
                m.value_measured as thickness,
                e.ambient_humidity_pct as humidity
            FROM lot_genealogy g
            JOIN final_yield_log y ON g.lot_id = y.lot_id
            JOIN process_cvd_log c ON g.lot_id = c.lot_id
            JOIN process_litho_log l ON g.lot_id = l.lot_id
            JOIN metrology_inline m ON g.lot_id = m.lot_id
            JOIN site_environment_log e ON DATE_FORMAT(g.end_time, '%Y-%m-%d %H') = DATE_FORMAT(e.timestamp, '%Y-%m-%d %H')
            ORDER BY g.end_time DESC
            LIMIT 500;
            """
            print("Executing query (this might take up to 2 minutes)...")
            cursor.execute(query)
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            
            if not df.empty:
                cols = ['yield_percentage', 'cvd_temp', 'target_temp', 'litho_focus', 'thickness', 'humidity']
                df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
                
                print(f"Fetched {len(df)} records. Saving to SQLite...")
                sqlite_db_path = os.path.join(script_dir, "local_data.db")
                sqlite_conn = sqlite3.connect(sqlite_db_path)
                df.to_sql('digital_twin_data', sqlite_conn, if_exists='replace', index=False)
                sqlite_conn.close()
                print("Cache updated successfully.")
            else:
                print("No data fetched from MySQL.")
    except Exception as e:
        print(f"Error updating cache: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    update_cache()
