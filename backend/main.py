# backend/main.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from datetime import datetime
from typing import Dict
from fastapi.middleware.cors import CORSMiddleware

DB_NAME = os.getenv("DB_NAME", "monitoring_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

app = FastAPI(title="Data Ingestion & Dashboard API", version="4.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DeviceReading(BaseModel):
    device_name: str
    readings: Dict[str, float]

def get_db_connection():
    try:
        return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
    except psycopg2.OperationalError as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e}")

def check_and_generate_alerts(cursor, device_id, readings, current_time):
    if 'transformer_temp' in readings and readings['transformer_temp'] > 90.0:
        msg = f"High Transformer Temp: {readings['transformer_temp']:.2f}°C"
        cursor.execute("INSERT INTO alerts (device_id, time, message, severity) VALUES (%s, %s, %s, %s);", (device_id, current_time, msg, 'ERROR'))
    if 'water_ph' in readings and (readings['water_ph'] < 6.0 or readings['water_ph'] > 9.0):
        msg = f"Abnormal Water pH: {readings['water_ph']:.2f}"
        cursor.execute("INSERT INTO alerts (device_id, time, message, severity) VALUES (%s, %s, %s, %s);", (device_id, current_time, msg, 'WARNING'))

@app.post("/ingest/")
def ingest_data(reading: DeviceReading):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT device_id FROM devices WHERE device_name = %s;", (reading.device_name,))
            device_record = cursor.fetchone()
            if not device_record: return {"status": "error", "message": f"Device '{reading.device_name}' not found."}
            device_id = device_record[0]

            param_names = tuple(reading.readings.keys())
            cursor.execute("SELECT param_name, param_id FROM parameters WHERE param_name IN %s;", (param_names,))
            param_map = {name: id for name, id in cursor.fetchall()}

            current_time = datetime.utcnow()
            insert_query = "INSERT INTO readings (time, device_id, param_id, param_value) VALUES (%s, %s, %s, %s);"
            for param_name, param_value in reading.readings.items():
                if param_name in param_map:
                    cursor.execute(insert_query, (current_time, device_id, param_map[param_name], param_value))
            
            check_and_generate_alerts(cursor, device_id, reading.readings, current_time)
        conn.commit()
        return {"status": "success"}
    except Exception as e:
        conn.rollback(); raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        conn.close()

@app.get("/devices")
def get_devices():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT dt.type_name, d.device_name FROM devices d JOIN device_types dt ON d.device_type_id = dt.type_id ORDER BY dt.type_name, d.device_name;")
            devices_by_type = {}
            for type_name, device_name in cursor.fetchall():
                if type_name not in devices_by_type: devices_by_type[type_name] = []
                devices_by_type[type_name].append(device_name)
        return devices_by_type
    finally:
        conn.close()

@app.get("/devices/{device_name}/analytics")
def get_device_analytics(device_name: str):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT device_id FROM devices WHERE device_name = %s;", (device_name,))
            device_record = cursor.fetchone();
            if not device_record: raise HTTPException(status_code=404, detail="Device not found")
            device_id = device_record[0]

            # Latest metrics
            cursor.execute("SELECT p.param_name, r.param_value, p.param_unit FROM (SELECT param_id, MAX(time) as max_time FROM readings WHERE device_id = %s GROUP BY param_id) as latest JOIN readings r ON r.param_id = latest.param_id AND r.time = latest.max_time JOIN parameters p ON p.param_id = r.param_id WHERE r.device_id = %s;", (device_id, device_id))
            latest_metrics = {name: f"{value:.2f} {unit if unit else ''}".strip() for name, value, unit in cursor.fetchall()}

            # 24-hour raw readings for trends
            trends_query = """
                SELECT r.time, p.param_name, r.param_value
                FROM readings r
                JOIN parameters p ON p.param_id = r.param_id
                WHERE r.device_id = %s AND r.time > NOW() - INTERVAL '24 hours'
                ORDER BY r.time ASC;
            """
            cursor.execute(trends_query, (device_id,))
            trends_result = cursor.fetchall()
            
            datasets = {}
            for time_val, param_name, param_value in trends_result:
                if param_name not in datasets:
                    datasets[param_name] = {"label": param_name, "data": []}
                if param_value is not None:
                    datasets[param_name]["data"].append({"x": time_val.isoformat(), "y": round(float(param_value), 2)})
            
            trends_chart_data = {"datasets": list(datasets.values())}

            # 7-day daily averages table
            cursor.execute("SELECT time_bucket('1 day', time)::date as day, p.param_name, AVG(r.param_value) as daily_avg FROM readings r JOIN parameters p ON p.param_id = r.param_id WHERE r.device_id = %s AND r.time > NOW() - INTERVAL '7 days' GROUP BY day, p.param_name ORDER BY day DESC, p.param_name;", (device_id,))
            daily_avg_data = cursor.fetchall()
            
            # Overall 7-day average
            cursor.execute("SELECT p.param_name, AVG(r.param_value), p.param_unit FROM readings r JOIN parameters p ON p.param_id = r.param_id WHERE r.device_id = %s AND r.time > NOW() - INTERVAL '7 days' GROUP BY p.param_name, p.param_unit;", (device_id,))
            overall_weekly_averages = {name: f"{value:.2f} {unit if unit else ''}".strip() for name, value, unit in cursor.fetchall()}

            return {"latest_metrics": latest_metrics, "trends": trends_chart_data, "daily_averages_table": daily_avg_data, "overall_weekly_averages": overall_weekly_averages}
    finally:
        conn.close()

@app.get("/alerts")
def get_alerts():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT a.time, d.device_name, a.message, a.severity FROM alerts a JOIN devices d ON a.device_id = d.device_id ORDER BY a.time DESC LIMIT 100;")
            return [{"time": t.isoformat(), "device_name": n, "message": m, "severity": s} for t, n, m, s in cursor.fetchall()]
    finally:
        conn.close()