import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

sql_commands = """
DROP DATABASE IF EXISTS Fab18;
CREATE DATABASE Fab18;
USE Fab18;

DROP TABLE IF EXISTS site_environment_log CASCADE;
CREATE TABLE site_environment_log (
    timestamp VARCHAR(255) PRIMARY KEY,
    ambient_temp_c VARCHAR(255),
    ambient_humidity_pct VARCHAR(255),
    vibration_index VARCHAR(255)
);

DROP TABLE IF EXISTS lot_genealogy CASCADE;
CREATE TABLE lot_genealogy (
    lot_id VARCHAR(255) PRIMARY KEY,
    product_type VARCHAR(255),
    start_time VARCHAR(255),
    end_time VARCHAR(255),
    current_status VARCHAR(255)
);

DROP TABLE IF EXISTS process_cvd_log CASCADE;
CREATE TABLE process_cvd_log (
    run_id VARCHAR(255) PRIMARY KEY,
    lot_id VARCHAR(255) REFERENCES lot_genealogy(lot_id),
    recipe_target_temp VARCHAR(255),
    actual_temp VARCHAR(255),
    chamber_pressure VARCHAR(255),
    gas_flow_rate VARCHAR(255)
);

DROP TABLE IF EXISTS process_litho_log CASCADE;
CREATE TABLE process_litho_log (
    run_id VARCHAR(255) PRIMARY KEY,
    lot_id VARCHAR(255) REFERENCES lot_genealogy(lot_id),
    focus_offset VARCHAR(255),
    exposure_dose_energy VARCHAR(255),
    alignment_accuracy_x VARCHAR(255),
    alignment_accuracy_y VARCHAR(255)
);

DROP TABLE IF EXISTS process_etch_log CASCADE;
CREATE TABLE process_etch_log (
    run_id VARCHAR(255) PRIMARY KEY,
    lot_id VARCHAR(255) REFERENCES lot_genealogy(lot_id),
    rf_power_forward VARCHAR(255),
    rf_power_reflected VARCHAR(255),
    etch_time_seconds VARCHAR(255),
    chamber_wall_temp VARCHAR(255)
);

DROP TABLE IF EXISTS metrology_inline CASCADE;
CREATE TABLE metrology_inline (
    run_id VARCHAR(255) PRIMARY KEY,
    lot_id VARCHAR(255) REFERENCES lot_genealogy(lot_id),
    step_name VARCHAR(255),
    measurement_name VARCHAR(255),
    value_measured VARCHAR(255)
);

DROP TABLE IF EXISTS final_yield_log CASCADE;
CREATE TABLE final_yield_log (
    lot_id VARCHAR(255) PRIMARY KEY REFERENCES lot_genealogy(lot_id),
    total_good_chips VARCHAR(255),
    total_bad_chips VARCHAR(255),
    yield_percentage VARCHAR(255),
    bin_code VARCHAR(255)
);

"""

def setup_database():
    timeout = 10
    connection = pymysql.connect(
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
    try:
        cursor = connection.cursor()
        statements = [s.strip() for s in sql_commands.split(';') if s.strip()]
        for statement in statements:
            cursor.execute(statement)
        print("Database and tables created successfully.")
    except pymysql.MySQLError as err:
        print(f" MySQL error: {err}")
    finally:
        if cursor:
            cursor.close()
        connection.close()

if __name__ == "__main__":
    setup_database()


