# FabSi 2.0: Semiconductor Fab Digital Twin

**FabSi 2.0** is the next evolution of the original [FabSi](https://github.com/11mosfets/FabSi) repository. It provides a robust, real-time simulation of a semiconductor fabrication plant, generating telemetry data, storing it in a SQL database, and visualizing it through a live Digital Twin dashboard.

## 🚀 Key Features

*   **Advanced Simulation**: Generates realistic time-series data for multiple fab processes:
    *   **Environment**: Temperature, Humidity, Vibration.
    *   **Genealogy**: Lot tracking (Start/End times, Status).
    *   **Process Logs**: CVD (Temp/Pressure/Gas), Lithography (Focus/Dose/Alignment), Etch (Power/Time).
    *   **Metrology**: Inline thickness measurements.
    *   **Yield**: Final good/bad chip counts and binning.
*   **Dual Data Modes**:
    *   **Historical**: Backfills data for the past 9 days (T-9 to T-2).
    *   **Daily**: Simulates the most recent completed day (T-2 to T-1) for daily automated runs.
*   **Real Weather Integration**: Uses Open-Meteo API to fetch real historical weather data to drive environmental constants.
*   **SQL Integration**: Automated schema creation and data loading into MySQL (compatible with Aiven, AWS RDS, etc.).
*   **Live Digital Twin**: Interactive Streamlit dashboard for real-time monitoring, SPC (Statistical Process Control) charting, and excursion analysis.

## 🛠️ Setup & Replication

Follow these steps to set up the environment and run the full pipeline.

### 1. Environment Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration (`.env`)

Create a `.env` file in the root directory to store your database credentials. This file is ignored by git for security.

```ini
DB_HOST=your-db-host
DB_PORT=23001
DB_USER=your-db-user
DB_PASS=your-db-password
DB_NAME=defaultdb
```

### 3. Database Initialization

Run the creator script to set up the schema and tables (Fab18 database).

```bash
python database_creator.py
```

### 4. Data Generation

Generate the datasets. These scripts output JSON files to the `jsons/` directory.

```bash
# 1. Generate Historical Data (T-9 days to T-2 days)
python data_7days.py

# 2. Generate Daily Data (T-2 days to T-1 day)
python data_day.py
```

### 5. Data Loading

Load the generated data into your MySQL database. This script automatically detects the correct file logic.

```bash
python jsontosql.py
```

### 6. Launch Dashboard

Start the live Digital Twin interface.

```bash
streamlit run app.py
```

## 🔒 Security

*   **Credentials**: Never hardcoded. Managed via `.env` locally and `st.secrets` for Streamlit Cloud deployment.
*   **Git**: `.env` and `.streamlit/secrets.toml` are included in `.gitignore` to prevent leakage.

## 📄 License

This project serves as a demonstration and educational tool for semiconductor manufacturing data analytics.
