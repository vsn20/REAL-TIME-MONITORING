-- Create the extension for TimescaleDB
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Table for storing device metadata
CREATE TABLE devices (
    device_id SERIAL PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100),
    install_date DATE DEFAULT CURRENT_DATE
);

-- Table for storing time-series readings
CREATE TABLE readings (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    power_consumption DOUBLE PRECISION,
    status VARCHAR(20),
    FOREIGN KEY (device_id) REFERENCES devices (device_id)
);

-- Convert 'readings' into a TimescaleDB hypertable for performance
SELECT create_hypertable('readings', 'time');

-- Table for storing generated alerts
CREATE TABLE alerts (
    alert_id SERIAL PRIMARY KEY,
    device_id INT NOT NULL,
    time TIMESTAMPTZ NOT NULL,
    message VARCHAR(255),
    severity VARCHAR(20), -- e.g., 'WARNING', 'ERROR'
    acknowledged BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (device_id) REFERENCES devices (device_id)
);

-- Pre-populate the devices table with 20 devices
INSERT INTO devices (device_name, location) VALUES
('Device_01', 'Factory A'), ('Device_02', 'Factory A'), ('Device_03', 'Factory A'), ('Device_04', 'Factory A'), ('Device_05', 'Factory A'),
('Device_06', 'Factory B'), ('Device_07', 'Factory B'), ('Device_08', 'Factory B'), ('Device_09', 'Factory B'), ('Device_10', 'Factory B'),
('Device_11', 'Warehouse X'), ('Device_12', 'Warehouse X'), ('Device_13', 'Warehouse X'), ('Device_14', 'Warehouse X'), ('Device_15', 'Warehouse X'),
('Device_16', 'Warehouse Y'), ('Device_17', 'Warehouse Y'), ('Device_18', 'Warehouse Y'), ('Device_19', 'Warehouse Y'), ('Device_20', 'Warehouse Y');