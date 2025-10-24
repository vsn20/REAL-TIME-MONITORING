# backend/main.py
import os
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import psycopg2
from datetime import datetime, timedelta # Import timedelta
from typing import Dict, Optional # Import Optional
from fastapi.middleware.cors import CORSMiddleware

DB_NAME = os.getenv("DB_NAME", "monitoring_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

app = FastAPI(title="Data Ingestion & Dashboard API", version="4.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Allow your React app origin
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
    # Alert generation logic (keep existing logic)
    if 'transformer_temp' in readings and readings['transformer_temp'] > 90.0:
        msg = f"High Transformer Temp: {readings['transformer_temp']:.2f}°C"
        # Check if a similar alert exists recently to avoid duplicates (optional)
        cursor.execute("""
            INSERT INTO alerts (device_id, time, message, severity)
            SELECT %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM alerts
                WHERE device_id = %s AND severity = 'ERROR' AND message LIKE 'High Transformer Temp%%'
                AND time > NOW() - INTERVAL '5 minutes'
            );
        """, (device_id, current_time, msg, 'ERROR', device_id))
    if 'water_ph' in readings and (readings['water_ph'] < 6.0 or readings['water_ph'] > 9.0):
        msg = f"Abnormal Water pH: {readings['water_ph']:.2f}"
        # Check if a similar alert exists recently (optional)
        cursor.execute("""
            INSERT INTO alerts (device_id, time, message, severity)
            SELECT %s, %s, %s, %s
            WHERE NOT EXISTS (
                SELECT 1 FROM alerts
                WHERE device_id = %s AND severity = 'WARNING' AND message LIKE 'Abnormal Water pH%%'
                AND time > NOW() - INTERVAL '5 minutes'
            );
        """, (device_id, current_time, msg, 'WARNING', device_id))


@app.post("/ingest/")
def ingest_data(reading: DeviceReading):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # Check if device exists
            cursor.execute("SELECT device_id FROM devices WHERE device_name = %s;", (reading.device_name,))
            device_record = cursor.fetchone()
            if not device_record:
                # Optionally, you could create the device here if it doesn't exist
                # For now, return error
                # return {"status": "error", "message": f"Device '{reading.device_name}' not found."}
                 raise HTTPException(status_code=404, detail=f"Device '{reading.device_name}' not found.")


            device_id = device_record[0]

            # Get parameter IDs
            param_names = tuple(reading.readings.keys())
            if not param_names:
                 return {"status": "success", "message": "No readings provided."} # Handle empty readings


            cursor.execute("SELECT param_name, param_id FROM parameters WHERE param_name IN %s;", (param_names,))
            param_map = {name: id for name, id in cursor.fetchall()}

            # Check for missing parameters and handle them (optional: log or raise error)
            missing_params = set(param_names) - set(param_map.keys())
            if missing_params:
                print(f"Warning: Parameters not found in DB for device {reading.device_name}: {missing_params}")
                # Decide how to handle: skip them, error out, etc.

            current_time = datetime.utcnow()
            insert_query = "INSERT INTO readings (time, device_id, param_id, param_value) VALUES (%s, %s, %s, %s);"

            values_to_insert = []
            for param_name, param_value in reading.readings.items():
                if param_name in param_map:
                     # Basic type check
                     if isinstance(param_value, (int, float)):
                         values_to_insert.append((current_time, device_id, param_map[param_name], param_value))
                     else:
                          print(f"Warning: Invalid value type for {param_name} in device {reading.device_name}. Expected number, got {type(param_value)}. Skipping.")

            if values_to_insert:
                 # Use execute_batch for potentially better performance with many readings
                 # For simplicity here, sticking with execute
                 for values in values_to_insert:
                     cursor.execute(insert_query, values)

            # Check for alerts after inserting valid readings
            check_and_generate_alerts(cursor, device_id, reading.readings, current_time)

        conn.commit()
        return {"status": "success"}
    except psycopg2.Error as db_error:
         conn.rollback()
         print(f"Database Error: {db_error}")
         raise HTTPException(status_code=500, detail=f"Database error occurred: {db_error}")
    except Exception as e:
        conn.rollback()
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

@app.get("/devices")
def get_devices():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT dt.type_name, d.device_name
                FROM devices d
                JOIN device_types dt ON d.device_type_id = dt.type_id
                ORDER BY dt.type_name, d.device_id; -- Order by ID for consistency
            """)
            devices_by_type = {}
            for type_name, device_name in cursor.fetchall():
                if type_name not in devices_by_type:
                    devices_by_type[type_name] = []
                devices_by_type[type_name].append(device_name)
        return devices_by_type
    finally:
        conn.close()

# Update the function signature to accept optional datetime query parameters
@app.get("/devices/{device_name}/analytics")
def get_device_analytics(
    device_name: str,
    start_time: Optional[datetime] = Query(None, description="Start time for data range (ISO format)"),
    end_time: Optional[datetime] = Query(None, description="End time for data range (ISO format)")
):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT device_id FROM devices WHERE device_name = %s;", (device_name,))
            device_record = cursor.fetchone()
            if not device_record:
                raise HTTPException(status_code=404, detail="Device not found")
            device_id = device_record[0]

            # --- Latest metrics (unaffected by time range) ---
            cursor.execute("""
                SELECT p.param_name, r.param_value, p.param_unit
                FROM (
                    SELECT param_id, MAX(time) as max_time
                    FROM readings
                    WHERE device_id = %s
                    GROUP BY param_id
                ) as latest
                JOIN readings r ON r.param_id = latest.param_id AND r.time = latest.max_time AND r.device_id = %s
                JOIN parameters p ON p.param_id = r.param_id;
            """, (device_id, device_id))
            latest_metrics = {name: f"{value:.2f} {unit if unit else ''}".strip() for name, value, unit in cursor.fetchall()}

            # --- Time-filtered data ---
            # Set default time range if not provided (e.g., last 24 hours)
            if end_time is None:
                end_time = datetime.utcnow()
            if start_time is None:
                start_time = end_time - timedelta(hours=24)

            # --- Trends data (filtered) ---
            trends_query = """
                SELECT r.time, p.param_name, r.param_value
                FROM readings r
                JOIN parameters p ON p.param_id = r.param_id
                WHERE r.device_id = %s AND r.time >= %s AND r.time <= %s
                ORDER BY r.time ASC;
            """
            cursor.execute(trends_query, (device_id, start_time, end_time))
            trends_result = cursor.fetchall()

            datasets = {}
            for time_val, param_name, param_value in trends_result:
                if param_name not in datasets:
                    datasets[param_name] = {"label": param_name.replace('_', ' ').title(), "data": []} # Format label
                if param_value is not None:
                    # Ensure timezone-aware ISO format string for JavaScript compatibility
                    time_str = time_val.isoformat(timespec='milliseconds') + 'Z'
                    datasets[param_name]["data"].append({"x": time_str, "y": round(float(param_value), 2)})

            trends_chart_data = {"datasets": list(datasets.values())}


             # --- Daily averages table (filtered, max 7 days within range) ---
            # Adjust start time for daily averages if range is longer than 7 days
            daily_avg_start_time = max(start_time, end_time - timedelta(days=7))

            cursor.execute("""
                SELECT time_bucket('1 day', time)::date as day, p.param_name, AVG(r.param_value) as daily_avg
                FROM readings r JOIN parameters p ON p.param_id = r.param_id
                WHERE r.device_id = %s AND r.time >= %s AND r.time <= %s
                GROUP BY day, p.param_name
                ORDER BY day DESC, p.param_name;
            """, (device_id, daily_avg_start_time, end_time))
            daily_avg_data = cursor.fetchall() # Keep original format for potential frontend processing

            # --- Overall averages for the selected period ---
            cursor.execute("""
                 SELECT p.param_name, AVG(r.param_value), p.param_unit
                 FROM readings r JOIN parameters p ON p.param_id = r.param_id
                 WHERE r.device_id = %s AND r.time >= %s AND r.time <= %s
                 GROUP BY p.param_name, p.param_unit;
             """, (device_id, start_time, end_time))
            overall_period_averages = {name: f"{value:.2f} {unit if unit else ''}".strip() for name, value, unit in cursor.fetchall()}


            return {
                "latest_metrics": latest_metrics,
                "trends": trends_chart_data,
                "daily_averages_table": daily_avg_data,
                 "overall_period_averages": overall_period_averages # Renamed from weekly
            }
    except psycopg2.Error as db_error:
         print(f"Database Error: {db_error}")
         raise HTTPException(status_code=500, detail=f"Database error occurred: {db_error}")
    except Exception as e:
        print(f"General Error: {e}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

# Update alerts endpoint to accept optional time range
@app.get("/alerts")
def get_alerts(
    start_time: Optional[datetime] = Query(None, description="Start time for alerts (ISO format)"),
    end_time: Optional[datetime] = Query(None, description="End time for alerts (ISO format)"),
    limit: int = Query(100, description="Maximum number of alerts to return") # Add limit parameter
):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT a.time, d.device_name, a.message, a.severity, p.param_name, a.alert_id
                FROM alerts a
                JOIN devices d ON a.device_id = d.device_id
                LEFT JOIN parameters p ON LOWER(a.message) LIKE LOWER(p.param_name || '%%') -- Basic attempt to link alert to a param
                WHERE 1=1
            """
            params = []
            if start_time:
                query += " AND a.time >= %s"
                params.append(start_time)
            if end_time:
                query += " AND a.time <= %s"
                params.append(end_time)

            query += " ORDER BY a.time DESC LIMIT %s;"
            params.append(limit)

            cursor.execute(query, tuple(params))
            # Include param_name and alert_id in the response
            return [{"time": t.isoformat(), "device_name": n, "message": m, "severity": s, "param_name": pn, "id": aid}
                    for t, n, m, s, pn, aid in cursor.fetchall()]
    except psycopg2.Error as db_error:
         print(f"Database Error: {db_error}")
         raise HTTPException(status_code=500, detail=f"Database error occurred: {db_error}")
    finally:
        if conn:
            conn.close()

# Optional: Add an endpoint to acknowledge alerts if needed
@app.put("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE alerts SET acknowledged = TRUE WHERE alert_id = %s RETURNING alert_id;", (alert_id,))
            updated = cursor.fetchone()
        conn.commit()
        if updated:
            return {"status": "success", "alert_id": updated[0]}
        else:
            raise HTTPException(status_code=404, detail="Alert not found")
    except psycopg2.Error as db_error:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {db_error}")
    finally:
        if conn:
            conn.close()