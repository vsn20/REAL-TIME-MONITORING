# Real-Time Operations Monitoring System

This project is a complete system for ingesting, storing, and visualizing real-time data from multiple devices, built with FastAPI, TimescaleDB, and Streamlit.

### Prerequisites

- **Docker & Docker Compose:** To run the database. [Install Docker](https://docs.docker.com/get-docker/)
- **Python 3.8+ & pip:** To run the application components.

### 🚀 How to Run the Project

Follow these steps in order.

#### Step 1: Start the Database

Open a terminal in the root `real-time-monitoring/` directory and run:

```bash
docker-compose up -d
```

This command will download the TimescaleDB image, start the database container in the background, and automatically run the `init.sql` script to create your tables and devices.

* To check if it's running, use `docker ps`. You should see a container named `timescaledb`.
* To stop the database, run `docker-compose down`.

#### Step 2: Install Python Dependencies

You need to install the required Python packages for each component. Open three separate terminals, all in the root `real-time-monitoring/` directory.

In **Terminal 1 (for the Backend)**:

```bash
pip install -r backend/requirements.txt
```

In **Terminal 2 (for the Simulator)**:

```bash
pip install -r simulator/requirements.txt
```

In **Terminal 3 (for the Dashboard)**:

```bash
pip install -r dashboard/requirements.txt
```

#### Step 3: Run the Application Components

Now, run each part of the system in its dedicated terminal.

In **Terminal 1 (Backend API)**, run:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

> You should see a message indicating the Uvicorn server is running. You can access the API docs at `http://localhost:8000/docs`.

In **Terminal 2 (Device Simulator)**, run:

```bash
python simulator/simulator.py
```

> You will see log messages as the simulator starts sending data to the backend API every 10 seconds.

In **Terminal 3 (Dashboard)**, run:

```bash
streamlit run dashboard/dashboard.py
```

> This will automatically open a new tab in your web browser with the dashboard, usually at `http://localhost:8501`.

### ✅ You're Done!

Your complete real-time monitoring system is now running.
- The **simulator** is generating data.
- The **backend** is receiving and storing it in **TimescaleDB**.
- The **dashboard** is visualizing the data.

Select different devices from the sidebar in the Streamlit dashboard to see their live metrics and historical trends. The data will update as new readings flow in.