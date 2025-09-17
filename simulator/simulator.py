# simulator/simulator.py
import requests
import random
import time
import schedule
import logging
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
API_URL = "http://127.0.0.1:8000/ingest/"
NUM_DEVICES = 200
SEND_INTERVAL_SECONDS = 10

DEVICE_TYPES = {
    "Energy": {
        "params": ['voltage', 'current', 'power_consumption', 'power_factor', 'frequency', 'phase_angle', 'reactive_power', 'apparent_power', 'line_to_line_voltage', 'line_to_neutral_voltage', 'circuit_breaker_status', 'transformer_temp'],
        "ranges": [(210, 240), (0.5, 15), (0.1, 5), (0.8, 1.0), (49.9, 50.1), (0, 30), (0, 2), (0.1, 6), (380, 415), (220, 240), (0, 1), (50, 90)]
    },
    "Water": {
        "params": ['water_flow_rate', 'water_pressure', 'water_ph', 'turbidity', 'conductivity', 'dissolved_oxygen', 'water_temperature', 'chlorine_level', 'valve_status', 'pump_speed', 'reservoir_level'],
        "ranges": [(5, 50), (1, 5), (6.5, 8.5), (0, 10), (100, 1000), (4, 10), (10, 30), (0.2, 2), (0, 1), (1000, 3000), (20, 100)]
    },
    "Weather": {
        "params": ['air_temperature', 'humidity', 'wind_speed', 'wind_direction', 'rainfall', 'air_pressure', 'solar_radiation', 'uv_index', 'dew_point', 'cloud_cover', 'visibility', 'lightning_detected'],
        "ranges": [(-10, 40), (20, 100), (0, 30), (0, 360), (0, 10), (980, 1050), (0, 1000), (0, 11), (-10, 25), (0, 100), (1, 20), (0, 1)]
    },
    "Atmosphere": {
        "params": ['co2_level', 'air_quality_index', 'o3_level', 'no2_level', 'so2_level', 'co_level', 'pm25_concentration', 'pm10_concentration', 'volatile_organic_compounds', 'radon_level', 'ambient_noise', 'pollen_count', 'mold_level'],
        "ranges": [(400, 2000), (0, 500), (0, 100), (0, 50), (0, 20), (0, 10), (0, 100), (0, 150), (0, 500), (0, 4), (30, 90), (0, 1000), (0, 500)]
    }
}

DEVICES = []
for i in range(1, 81): DEVICES.append({"name": f"Device_{i:03d}", "type": "Energy"})
for i in range(81, 131): DEVICES.append({"name": f"Device_{i:03d}", "type": "Water"})
for i in range(131, 166): DEVICES.append({"name": f"Device_{i:03d}", "type": "Weather"})
for i in range(166, 201): DEVICES.append({"name": f"Device_{i:03d}", "type": "Atmosphere"})


def send_data(device):
    device_type_info = DEVICE_TYPES[device["type"]]
    readings = {}
    for i, param in enumerate(device_type_info["params"]):
        min_val, max_val = device_type_info["ranges"][i]
        readings[param] = round(random.uniform(min_val, max_val), 2)

    # Intentionally trigger alerts sometimes
    if device['type'] == 'Energy' and random.random() < 0.05: # 5% chance
        readings['transformer_temp'] = round(random.uniform(95.0, 110.0), 2) # High temp
    if device['type'] == 'Water' and random.random() < 0.05:
        readings['water_ph'] = round(random.uniform(3.0, 5.0), 2) # Low pH

    data = {"device_name": device["name"], "readings": readings}

    try:
        response = requests.post(API_URL, json=data, timeout=5)
        if response.status_code != 200:
             logging.error(f"Error for {device['name']}: {response.text}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending data for {device['name']}: {e}")

def scheduled_job():
    logging.info("--- Sending batch of readings for all devices ---")
    threads = [threading.Thread(target=send_data, args=(device,)) for device in DEVICES]
    for thread in threads: thread.start()
    for thread in threads: thread.join()
    logging.info("--- Batch sent ---")

if __name__ == "__main__":
    logging.info(f"Device simulator started. Sending data every {SEND_INTERVAL_SECONDS} seconds.")
    schedule.every(SEND_INTERVAL_SECONDS).seconds.do(scheduled_job)
    scheduled_job()
    while True:
        schedule.run_pending()
        time.sleep(1)