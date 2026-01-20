import json
import random
import uuid
import requests
from datetime import datetime, timedelta

OUTPUT_FILE = "jsons/fab_full_dump.json"

def fetch_real_weather(days):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 33.44,
        "longitude": -112.07,
        "hourly": "temperature_2m,relative_humidity_2m",
        "past_days": days,
        "forecast_days": 1
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        hourly = data.get("hourly", {})
        count = days * 24
        
        return {
            "temp": hourly["temperature_2m"][-count:], 
            "humid": hourly["relative_humidity_2m"][-count:]
        }
    except Exception as e:
        print(f"Weather API unavailable: {e}. Using simulation.")
        return None

def generate_fab_dump(days=7):
    print(f"Generating {days} days of Fab Data...")

    weather_history = fetch_real_weather(days)
    
    data_dump = {
        "site_environment_log": [],
        "lot_genealogy": [],
        "process_cvd_log": [],
        "process_litho_log": [],
        "process_etch_log": [],
        "metrology_inline": [],
        "final_yield_log": []
    }

    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_time = now - timedelta(days=2)
    base_time = end_time - timedelta(days=days)
    total_hours = days * 24

    for hour in range(total_hours):
        current_time = base_time + timedelta(hours=hour)
        timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
        
        if weather_history and hour < len(weather_history["temp"]):
            temp = weather_history["temp"][hour]
            humidity = weather_history["humid"][hour]
        else:
            is_daytime = 6 <= current_time.hour <= 18
            temp = random.gauss(35, 5) if is_daytime else random.gauss(20, 3)
            humidity = random.gauss(15, 2) if is_daytime else random.gauss(25, 5)

        data_dump["site_environment_log"].append({
            "timestamp": timestamp_str,
            "ambient_temp_c": str(round(temp, 2)),
            "ambient_humidity_pct": str(round(humidity, 2)),
            "vibration_index": str(round(random.uniform(0, 10), 2))
        })

        lot_id = f"L2026-{str(hour).zfill(3)}"
        data_dump["lot_genealogy"].append({
            "lot_id": lot_id,
            "product_type": "Logic_5nm",
            "start_time": timestamp_str,
            "end_time": (current_time + timedelta(minutes=55)).strftime("%Y-%m-%d %H:%M:%S"),
            "current_status": "Completed"
        })

        drift = (hour * 0.1) if hour < 72 else 0 
        cvd_temp = 600 + drift + random.gauss(0, 1)
        
        data_dump["process_cvd_log"].append({
            "run_id": str(uuid.uuid4()),
            "lot_id": lot_id,
            "recipe_target_temp": "600",
            "actual_temp": str(round(cvd_temp, 2)),
            "chamber_pressure": str(round(40 + random.uniform(-1, 1), 2)),
            "gas_flow_rate": "200"
        })

        focus_error = (humidity - 20) * 0.5 if humidity > 20 else 0
        
        data_dump["process_litho_log"].append({
            "run_id": str(uuid.uuid4()),
            "lot_id": lot_id,
            "focus_offset": str(round(0 + focus_error + random.gauss(0, 2), 2)),
            "exposure_dose_energy": str(round(25 + random.uniform(-0.5, 0.5), 2)),
            "alignment_accuracy_x": str(round(random.uniform(-5, 5), 4)),
            "alignment_accuracy_y": str(round(random.uniform(-5, 5), 4))
        })

        chamber_temp = 60 + (temp * 0.1)
        
        data_dump["process_etch_log"].append({
            "run_id": str(uuid.uuid4()),
            "lot_id": lot_id,
            "rf_power_forward": "1500",
            "rf_power_reflected": str(round(random.uniform(0, 10), 2)),
            "etch_time_seconds": "120",
            "chamber_wall_temp": str(round(chamber_temp, 2))
        })

        thickness = 100 + (drift * 2) + random.gauss(0, 1)
        data_dump["metrology_inline"].append({
            "run_id": str(uuid.uuid4()),
            "lot_id": lot_id,
            "step_name": "Post-CVD",
            "measurement_name": "Thickness_A",
            "value_measured": str(round(thickness, 2))
        })

        base_yield = 98.0
        if thickness > 105:
            base_yield -= (thickness - 105) * 5
        if humidity > 40:
             base_yield -= (humidity - 40) * 0.5

        final_yield = max(0, min(100, base_yield + random.uniform(-1, 1)))
        
        data_dump["final_yield_log"].append({
            "lot_id": lot_id,
            "total_good_chips": str(int(final_yield * 10)),
            "total_bad_chips": str(int((100 - final_yield) * 10)),
            "yield_percentage": str(round(final_yield, 2)),
            "bin_code": "Bin 1" if final_yield > 90 else "Bin 0"
        })

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(data_dump, f, indent=2)
    
    print(f"Generated {OUTPUT_FILE} with {total_hours} hours of data.")

if __name__ == "__main__":
    generate_fab_dump(days=7)