import requests
import random
import time
import schedule
import logging

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
API_URL = "http://127.0.0.1:8000/ingest/"
DEVICE_NAMES = [f"Device_{i+1:02d}" for i in range(20)]
SEND_INTERVAL_SECONDS = 60 # Send data every 3000 seconds for demo purposes

def send_data(device_name):
    """Generates and sends a single data point for a device."""
    data = {
        "device_name": device_name,
        "temperature": round(random.uniform(20.0, 100.0), 2),
        "humidity": round(random.uniform(30.0, 90.0), 2),
        "power_consumption": round(random.uniform(0.5, 7.0), 2),
        "status": random.choice(['OK', 'OK', 'OK', 'OK', 'WARNING', 'ERROR'])
    }
    try:
        response = requests.post(API_URL, json=data, timeout=5)
        response.raise_for_status()
        logging.info(f"Successfully sent data for {device_name}.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending data for {device_name}: {e}")

def scheduled_job():
    """The main job that sends data for all devices."""
    logging.info("--- Sending batch of readings for all devices ---")
    for device in DEVICE_NAMES:
        send_data(device)

if __name__ == "__main__":
    logging.info(f"Device simulator started. Sending data every {SEND_INTERVAL_SECONDS} seconds.")
    # For actual 5-minute interval, use: schedule.every(5).minutes.do(scheduled_job)
    schedule.every(SEND_INTERVAL_SECONDS).seconds.do(scheduled_job)
    
    # Run once at the start
    scheduled_job()

    while True:
        schedule.run_pending()
        time.sleep(1)