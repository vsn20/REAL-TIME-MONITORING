import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from datetime import datetime

# --- Database Connection Details ---
# It's better to use environment variables in a real application
DB_NAME = os.getenv("DB_NAME", "monitoring_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# --- FastAPI App Initialization ---
app = FastAPI(title="Data Ingestion API", version="1.0")

# --- Pydantic Model for Incoming Data ---
class DeviceReading(BaseModel):
    device_name: str
    temperature: float
    humidity: float
    power_consumption: float
    status: str

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        return conn
    except psycopg2.OperationalError as e:
        # This helps in debugging connection issues
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e}")

@app.post("/ingest/")
def ingest_data(reading: DeviceReading):
    """
    Endpoint to ingest data from devices, store it, and check for alerts.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Get device_id from device_name
            cursor.execute("SELECT device_id FROM devices WHERE device_name = %s;", (reading.device_name,))
            device_record = cursor.fetchone()
            if not device_record:
                raise HTTPException(status_code=404, detail=f"Device '{reading.device_name}' not found.")
            device_id = device_record[0]

            # 2. Insert the new reading
            insert_query = """
                INSERT INTO readings (time, device_id, temperature, humidity, power_consumption, status)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            reading_data = (datetime.utcnow(), device_id, reading.temperature, reading.humidity, reading.power_consumption, reading.status)
            cursor.execute(insert_query, reading_data)
            
            # 3. Simple Alerting Logic
            if reading.temperature > 90.0:
                alert_msg = f"High Temperature Alert: {reading.temperature:.2f}°C"
                cursor.execute(
                    "INSERT INTO alerts (device_id, time, message, severity) VALUES (%s, %s, %s, %s);",
                    (device_id, datetime.utcnow(), alert_msg, 'ERROR')
                )
            if reading.power_consumption > 5.0:
                alert_msg = f"High Power Consumption: {reading.power_consumption:.2f} kWh"
                cursor.execute(
                    "INSERT INTO alerts (device_id, time, message, severity) VALUES (%s, %s, %s, %s);",
                    (device_id, datetime.utcnow(), alert_msg, 'WARNING')
                )
        
        conn.commit()
        return {"status": "success", "message": "Data ingested successfully"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        conn.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Data Ingestion API. Use the /docs endpoint to see the documentation."}