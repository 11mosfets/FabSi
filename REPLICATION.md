# Replication Guide

Follow these steps to set up the environment and run the data generation pipeline.

## 1. Environment Setup

Create a virtual environment:
python3 -m venv .venv

Activate the virtual environment:
source .venv/bin/activate

Install dependencies:
pip install -r requirements.txt

## 2. Database Setup

Run the database creator script to initialize the tables:
python database_creator.py

## 3. Data Generation

Generate the historical dataset (T-9 days to T-2 days):
python data_7days.py

Generate the daily dataset (T-2 days to T-1 day):
python data_day.py

The output files will be saved in the `jsons/` directory.

## 4. Data Loading

Load the historical data into the SQL database:
python jsontosql.py

## 5. Dashboard

Run the live digital twin dashboard:
streamlit run app.py
