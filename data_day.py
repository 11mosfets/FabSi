import json
import uuid
import random
import requests
from datetime import datetime, timedelta

FAB_LOCATION = {"lat": 33.44, "lon": -112.07}

def fetch_real_weather(days):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": FAB_LOCATION["lat"],
        "longitude": FAB_LOCATION["lon"],
        "hourly": "temperature_2m,relative_humidity_2m",
        "past_days": days,
        "forecast_days": 1
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        hourly = data.get("hourly", {})
        # We need flexible fetching, so return the whole lists
        return {
            "time": hourly.get("time", []),
            "temp": hourly.get("temperature_2m", []), 
            "humid": hourly.get("relative_humidity_2m", [])
        }
    except Exception as e:
        print(f"Weather API Unavailable: {e}. Using simulated values.")
        return None

def find_weather_index(weather_data, target_time):
    if not weather_data: return -1
    # API returns ISO strings like "2023-10-27T13:00"
    target_iso = target_time.strftime("%Y-%m-%dT%H:00")
    try:
        return weather_data["time"].index(target_iso)
    except ValueError:
        return -1

def generate_daily_dump():
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    start_time = now - timedelta(days=2)
    
    # OUTPUT_FILE = f"jsons/fab_data_{start_time.strftime('%Y-%m-%d')}.json"
    file_date = start_time.strftime("%Y-%m-%d")
    output_filename = f"jsons/fab_data_{file_date}.json"

    duration_hours = 24
    
    print(f"Generating Fab Data for: {file_date} (1 Day)")
    
    weather_history = fetch_real_weather(3)

    data_packet = {
        "site_environment_log": [],
        "lot_genealogy": [],
        "process_cvd_log": [],
        "process_litho_log": [],
        "process_etch_log": [],
        "metrology_inline": [],
        "final_yield_log": []
    }

    for hour in range(duration_hours):
        current_time = start_time + timedelta(hours=hour)
        timestamp_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

        idx = find_weather_index(weather_history, current_time)
        if idx != -1:
            temp = weather_history["temp"][idx]
            humid = weather_history["humid"][idx]
        else:
            is_daytime = 6 <= current_time.hour <= 18
            temp = random.gauss(35, 5) if is_daytime else random.gauss(20, 3)
            humid = random.gauss(15, 2) if is_daytime else random.gauss(25, 5)

        hour_marker = (current_time.timetuple().tm_yday * 24) + current_time.hour
        drift_cycle = hour_marker % 72 
        drift_val = (drift_cycle * 0.1) if drift_cycle < 60 else 0 

        data_packet["site_environment_log"].append({
            "timestamp": timestamp_str,
            "ambient_temp_c": str(temp),
            "ambient_humidity_pct": str(humid),
            "vibration_index": str(round(random.uniform(0.1, 2.5), 2))
        })

        lot_id = f"LLIVE-{current_time.strftime('%m%d-%H%M')}"
        data_packet["lot_genealogy"].append({
            "lot_id": lot_id,
            "product_type": "Logic_5nm",
            "start_time": timestamp_str,
            "end_time": timestamp_str,
            "current_status": "Completed"
        })

        cvd_temp = 600 + drift_val + random.gauss(0, 0.5)
        data_packet["process_cvd_log"].append({
            "run_id": str(uuid.uuid4()),
            "lot_id": lot_id,
            "recipe_target_temp": "600",
            "actual_temp": str(round(cvd_temp, 2)),
            "chamber_pressure": str(round(40 + random.uniform(-0.5, 0.5), 2)),
            "gas_flow_rate": "200"
        })

        humid_impact = (humid - 30) * 0.1 if humid > 30 else 0
        data_packet["process_litho_log"].append({
            "run_id": str(uuid.uuid4()),
            "lot_id": lot_id,
            "focus_offset": str(round(0 + humid_impact + random.gauss(0, 1), 2)),
            "exposure_dose_energy": "25",
            "alignment_accuracy_x": str(round(random.uniform(-3, 3), 3)),
            "alignment_accuracy_y": str(round(random.uniform(-3, 3), 3))
        })

        wall_temp = 60 + (temp * 0.2)
        data_packet["process_etch_log"].append({
            "run_id": str(uuid.uuid4()),
            "lot_id": lot_id,
            "rf_power_forward": "1500",
            "rf_power_reflected": str(round(random.uniform(0, 5), 2)),
            "etch_time_seconds": "120",
            "chamber_wall_temp": str(round(wall_temp, 2))
        })

        thickness = 100 + (drift_val * 1.5) + random.gauss(0, 1)
        data_packet["metrology_inline"].append({
            "run_id": str(uuid.uuid4()),
            "lot_id": lot_id,
            "step_name": "Post-CVD",
            "measurement_name": "Thickness_A",
            "value_measured": str(round(thickness, 2))
        })

        yield_penalty = 0
        if thickness > 105: yield_penalty += (thickness - 105) * 10
        if humid > 40: yield_penalty += 5

        final_yield = max(0, 99.5 - yield_penalty - random.uniform(0, 1))

        data_packet["final_yield_log"].append({
            "lot_id": lot_id,
            "total_good_chips": str(int(final_yield * 10)),
            "total_bad_chips": str(int((100 - final_yield) * 10)),
            "yield_percentage": str(round(final_yield, 2)),
            "bin_code": "Bin 1" if final_yield > 90 else "Bin 0"
        })

    with open(output_filename, 'w') as f:
        json.dump(data_packet, f, indent=2)
    
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    generate_daily_dump()