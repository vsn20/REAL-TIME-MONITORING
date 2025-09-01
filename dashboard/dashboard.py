import os
import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Real-Time Operations Dashboard",
    page_icon="🏭",
    layout="wide"
)

# --- Database Connection ---
@st.cache_resource
def get_db_connection():
    """Establishes a cached database connection."""
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "monitoring_db"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASS", "password"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432")
    )
    return conn

@st.cache_data(ttl=30) # Cache data for 30 seconds
def fetch_query(query, params=None):
    """Fetches data from the database and returns a DataFrame."""
    conn = get_db_connection()
    df = pd.read_sql(query, conn, params=params)
    return df

# --- Main Application ---
st.title("🏭 Real-Time Operations Dashboard")

# --- Sidebar Filters ---
device_list = fetch_query("SELECT device_name FROM devices ORDER BY device_name;")['device_name'].tolist()
selected_device = st.sidebar.selectbox("Select a Device", device_list)

# --- Auto-refresh control ---
st.sidebar.markdown("---")
if st.sidebar.button('Refresh Data'):
    st.cache_data.clear()
    st.rerun()

# --- Main Content ---
if selected_device:
    # 1. Key Metrics (Latest Reading)
    st.header(f"Live Status: {selected_device}")
    latest_reading_query = """
        SELECT time, temperature, humidity, power_consumption, status
        FROM readings r JOIN devices d ON r.device_id = d.device_id
        WHERE d.device_name = %(device)s
        ORDER BY time DESC LIMIT 1;
    """
    latest_reading = fetch_query(latest_reading_query, params={'device': selected_device})

    if not latest_reading.empty:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Temperature", f"{latest_reading['temperature'].iloc[0]:.1f} °C")
        col2.metric("Humidity", f"{latest_reading['humidity'].iloc[0]:.1f} %")
        col3.metric("Power", f"{latest_reading['power_consumption'].iloc[0]:.2f} kWh")
        col4.metric("Status", latest_reading['status'].iloc[0].upper())
    else:
        st.warning("No recent data available for this device.")

    st.markdown("---")

    # 2. Time-Series Trend Chart (Last 24 Hours)
    st.header("Historical Trends (Last 24 Hours)")
    trends_query = """
        SELECT time, temperature, humidity, power_consumption
        FROM readings r JOIN devices d ON r.device_id = d.device_id
        WHERE d.device_name = %(device)s AND time > NOW() - INTERVAL '24 hours'
        ORDER BY time;
    """
    trends_df = fetch_query(trends_query, params={'device': selected_device})

    if not trends_df.empty:
        trends_df_long = trends_df.melt(id_vars=['time'], value_vars=['temperature', 'humidity', 'power_consumption'])
        fig = px.line(trends_df_long, x='time', y='value', color='variable',
                      labels={'time': 'Time', 'value': 'Value', 'variable': 'Parameter'},
                      title=f"Sensor Readings for {selected_device}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data recorded in the last 24 hours for trend analysis.")

    st.markdown("---")
    
    # 3. Analytics: Daily Averages & Recent Alerts
    col1, col2 = st.columns(2)

    with col1:
        st.header("Daily Averages (Last 7 Days)")
        daily_avg_query = """
            SELECT
                time_bucket('1 day', time)::date AS day,
                ROUND(AVG(temperature)::numeric, 2) AS avg_temp,
                ROUND(AVG(power_consumption)::numeric, 2) AS avg_power
            FROM readings r JOIN devices d ON r.device_id = d.device_id
            WHERE d.device_name = %(device)s AND time > NOW() - INTERVAL '7 days'
            GROUP BY day ORDER BY day DESC;
        """
        daily_avg_df = fetch_query(daily_avg_query, params={'device': selected_device})
        st.dataframe(daily_avg_df, use_container_width=True)

    with col2:
        st.header("🚨 Recent Alerts (All Devices)")
        alerts_query = """
            SELECT a.time, d.device_name, a.message, a.severity
            FROM alerts a JOIN devices d ON a.device_id = d.device_id
            ORDER BY a.time DESC LIMIT 10;
        """
        alerts_df = fetch_query(alerts_query)
        st.dataframe(alerts_df, use_container_width=True)

else:
    st.info("Please select a device from the sidebar to view its data.")