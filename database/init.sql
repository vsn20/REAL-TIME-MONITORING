-- -- init.sql

-- CREATE EXTENSION IF NOT EXISTS timescaledb;

-- -- 1NF: Table for device types (e.g., Energy, Water, Weather)
-- CREATE TABLE device_types (
--     type_id SERIAL PRIMARY KEY,
--     type_name VARCHAR(50) NOT NULL UNIQUE
-- );

-- -- 1NF & 2NF: Lookup table for all possible parameters
-- CREATE TABLE parameters (
--     param_id SERIAL PRIMARY KEY,
--     param_name VARCHAR(50) NOT NULL UNIQUE,
--     param_unit VARCHAR(20)
-- );

-- -- 3NF: Main table for device metadata
-- CREATE TABLE devices (
--     device_id SERIAL PRIMARY KEY,
--     device_name VARCHAR(100) NOT NULL UNIQUE,
--     location VARCHAR(100),
--     install_date DATE DEFAULT CURRENT_DATE,
--     device_type_id INT,
--     FOREIGN KEY (device_type_id) REFERENCES device_types (type_id)
-- );

-- -- Table for the actual time-series readings
-- CREATE TABLE readings (
--     time TIMESTAMPTZ NOT NULL,
--     device_id INT NOT NULL,
--     param_id INT NOT NULL,
--     param_value DOUBLE PRECISION,
--     FOREIGN KEY (device_id) REFERENCES devices (device_id),
--     FOREIGN KEY (param_id) REFERENCES parameters (param_id),
--     PRIMARY KEY (time, device_id, param_id)
-- );

-- -- Convert 'readings' into a TimescaleDB hypertable
-- SELECT create_hypertable('readings', 'time');

-- -- Table for alerts
-- CREATE TABLE alerts (
--     alert_id SERIAL PRIMARY KEY,
--     device_id INT NOT NULL,
--     time TIMESTAMPTZ NOT NULL,
--     message VARCHAR(255),
--     severity VARCHAR(20),
--     acknowledged BOOLEAN DEFAULT FALSE,
--     FOREIGN KEY (device_id) REFERENCES devices (device_id)
-- );

-- -- Pre-populate the new lookup tables
-- INSERT INTO device_types (type_name) VALUES
-- ('Energy'), ('Water'), ('Weather'), ('Atmosphere');

-- INSERT INTO parameters (param_name, param_unit) VALUES
-- ('temperature', '°C'), ('humidity', '%'), ('power_consumption', 'kWh'),
-- ('voltage', 'V'), ('current', 'A'), ('power_factor', ''),
-- ('water_flow_rate', 'L/min'), ('water_pressure', 'bar'), ('water_ph', ''),
-- ('wind_speed', 'm/s'), ('wind_direction', '°'), ('rainfall', 'mm'),
-- ('air_pressure', 'hPa'), ('co2_level', 'ppm'), ('air_quality_index', '');

-- -- Pre-populate the devices table with 200 devices
-- INSERT INTO devices (device_name, location, device_type_id) VALUES
-- -- 80 Energy Devices (40%)
-- ('Device_001', 'Factory A', 1), ('Device_002', 'Factory A', 1), ('Device_003', 'Factory A', 1), ('Device_004', 'Factory A', 1), ('Device_005', 'Factory A', 1),
-- ('Device_006', 'Factory A', 1), ('Device_007', 'Factory A', 1), ('Device_008', 'Factory A', 1), ('Device_009', 'Factory A', 1), ('Device_010', 'Factory A', 1),
-- ('Device_011', 'Factory A', 1), ('Device_012', 'Factory A', 1), ('Device_013', 'Factory A', 1), ('Device_014', 'Factory A', 1), ('Device_015', 'Factory A', 1),
-- ('Device_016', 'Factory A', 1), ('Device_017', 'Factory A', 1), ('Device_018', 'Factory A', 1), ('Device_019', 'Factory A', 1), ('Device_020', 'Factory A', 1),
-- ('Device_021', 'Factory B', 1), ('Device_022', 'Factory B', 1), ('Device_023', 'Factory B', 1), ('Device_024', 'Factory B', 1), ('Device_025', 'Factory B', 1),
-- ('Device_026', 'Factory B', 1), ('Device_027', 'Factory B', 1), ('Device_028', 'Factory B', 1), ('Device_029', 'Factory B', 1), ('Device_030', 'Factory B', 1),
-- ('Device_031', 'Factory B', 1), ('Device_032', 'Factory B', 1), ('Device_033', 'Factory B', 1), ('Device_034', 'Factory B', 1), ('Device_035', 'Factory B', 1),
-- ('Device_036', 'Factory B', 1), ('Device_037', 'Factory B', 1), ('Device_038', 'Factory B', 1), ('Device_039', 'Factory B', 1), ('Device_040', 'Factory B', 1),
-- ('Device_041', 'Warehouse X', 1), ('Device_042', 'Warehouse X', 1), ('Device_043', 'Warehouse X', 1), ('Device_044', 'Warehouse X', 1), ('Device_045', 'Warehouse X', 1),
-- ('Device_046', 'Warehouse X', 1), ('Device_047', 'Warehouse X', 1), ('Device_048', 'Warehouse X', 1), ('Device_049', 'Warehouse X', 1), ('Device_050', 'Warehouse X', 1),
-- ('Device_051', 'Warehouse X', 1), ('Device_052', 'Warehouse X', 1), ('Device_053', 'Warehouse X', 1), ('Device_054', 'Warehouse X', 1), ('Device_055', 'Warehouse X', 1),
-- ('Device_056', 'Warehouse X', 1), ('Device_057', 'Warehouse X', 1), ('Device_058', 'Warehouse X', 1), ('Device_059', 'Warehouse X', 1), ('Device_060', 'Warehouse X', 1),
-- ('Device_061', 'Warehouse Y', 1), ('Device_062', 'Warehouse Y', 1), ('Device_063', 'Warehouse Y', 1), ('Device_064', 'Warehouse Y', 1), ('Device_065', 'Warehouse Y', 1),
-- ('Device_066', 'Warehouse Y', 1), ('Device_067', 'Warehouse Y', 1), ('Device_068', 'Warehouse Y', 1), ('Device_069', 'Warehouse Y', 1), ('Device_070', 'Warehouse Y', 1),
-- ('Device_071', 'Warehouse Y', 1), ('Device_072', 'Warehouse Y', 1), ('Device_073', 'Warehouse Y', 1), ('Device_074', 'Warehouse Y', 1), ('Device_075', 'Warehouse Y', 1),
-- ('Device_076', 'Warehouse Y', 1), ('Device_077', 'Warehouse Y', 1), ('Device_078', 'Warehouse Y', 1), ('Device_079', 'Warehouse Y', 1), ('Device_080', 'Warehouse Y', 1),

-- -- 50 Water Devices (25%)
-- ('Device_081', 'Factory A', 2), ('Device_082', 'Factory A', 2), ('Device_083', 'Factory A', 2), ('Device_084', 'Factory A', 2), ('Device_085', 'Factory A', 2),
-- ('Device_086', 'Factory A', 2), ('Device_087', 'Factory A', 2), ('Device_088', 'Factory A', 2), ('Device_089', 'Factory A', 2), ('Device_090', 'Factory A', 2),
-- ('Device_091', 'Factory B', 2), ('Device_092', 'Factory B', 2), ('Device_093', 'Factory B', 2), ('Device_094', 'Factory B', 2), ('Device_095', 'Factory B', 2),
-- ('Device_096', 'Factory B', 2), ('Device_097', 'Factory B', 2), ('Device_098', 'Factory B', 2), ('Device_099', 'Factory B', 2), ('Device_100', 'Factory B', 2),
-- ('Device_101', 'Factory B', 2), ('Device_102', 'Factory B', 2), ('Device_103', 'Factory B', 2), ('Device_104', 'Factory B', 2), ('Device_105', 'Factory B', 2),
-- ('Device_106', 'Warehouse X', 2), ('Device_107', 'Warehouse X', 2), ('Device_108', 'Warehouse X', 2), ('Device_109', 'Warehouse X', 2), ('Device_110', 'Warehouse X', 2),
-- ('Device_111', 'Warehouse X', 2), ('Device_112', 'Warehouse X', 2), ('Device_113', 'Warehouse X', 2), ('Device_114', 'Warehouse X', 2), ('Device_115', 'Warehouse X', 2),
-- ('Device_116', 'Warehouse Y', 2), ('Device_117', 'Warehouse Y', 2), ('Device_118', 'Warehouse Y', 2), ('Device_119', 'Warehouse Y', 2), ('Device_120', 'Warehouse Y', 2),
-- ('Device_121', 'Warehouse Y', 2), ('Device_122', 'Warehouse Y', 2), ('Device_123', 'Warehouse Y', 2), ('Device_124', 'Warehouse Y', 2), ('Device_125', 'Warehouse Y', 2),
-- ('Device_126', 'Warehouse Y', 2), ('Device_127', 'Warehouse Y', 2), ('Device_128', 'Warehouse Y', 2), ('Device_129', 'Warehouse Y', 2), ('Device_130', 'Warehouse Y', 2),

-- -- 35 Weather Devices
-- ('Device_131', 'Rooftop A', 3), ('Device_132', 'Rooftop A', 3), ('Device_133', 'Rooftop A', 3), ('Device_134', 'Rooftop A', 3), ('Device_135', 'Rooftop A', 3),
-- ('Device_136', 'Rooftop B', 3), ('Device_137', 'Rooftop B', 3), ('Device_138', 'Rooftop B', 3), ('Device_139', 'Rooftop B', 3), ('Device_140', 'Rooftop B', 3),
-- ('Device_141', 'Rooftop X', 3), ('Device_142', 'Rooftop X', 3), ('Device_143', 'Rooftop X', 3), ('Device_144', 'Rooftop X', 3), ('Device_145', 'Rooftop X', 3),
-- ('Device_146', 'Rooftop Y', 3), ('Device_147', 'Rooftop Y', 3), ('Device_148', 'Rooftop Y', 3), ('Device_149', 'Rooftop Y', 3), ('Device_150', 'Rooftop Y', 3),
-- ('Device_151', 'Field 1', 3), ('Device_152', 'Field 1', 3), ('Device_153', 'Field 1', 3), ('Device_154', 'Field 1', 3), ('Device_155', 'Field 1', 3),
-- ('Device_156', 'Field 2', 3), ('Device_157', 'Field 2', 3), ('Device_158', 'Field 2', 3), ('Device_159', 'Field 2', 3), ('Device_160', 'Field 2', 3),
-- ('Device_161', 'Field 3', 3), ('Device_162', 'Field 3', 3), ('Device_163', 'Field 3', 3), ('Device_164', 'Field 3', 3), ('Device_165', 'Field 3', 3),

-- -- 35 Atmosphere Devices
-- ('Device_166', 'Lab A', 4), ('Device_167', 'Lab A', 4), ('Device_168', 'Lab A', 4), ('Device_169', 'Lab A', 4), ('Device_170', 'Lab A', 4),
-- ('Device_171', 'Lab B', 4), ('Device_172', 'Lab B', 4), ('Device_173', 'Lab B', 4), ('Device_174', 'Lab B', 4), ('Device_175', 'Lab B', 4),
-- ('Device_176', 'Cleanroom X', 4), ('Device_177', 'Cleanroom X', 4), ('Device_178', 'Cleanroom X', 4), ('Device_179', 'Cleanroom X', 4), ('Device_180', 'Cleanroom X', 4),
-- ('Device_181', 'Cleanroom Y', 4), ('Device_182', 'Cleanroom Y', 4), ('Device_183', 'Cleanroom Y', 4), ('Device_184', 'Cleanroom Y', 4), ('Device_185', 'Cleanroom Y', 4),
-- ('Device_186', 'Office 1', 4), ('Device_187', 'Office 1', 4), ('Device_188', 'Office 1', 4), ('Device_189', 'Office 1', 4), ('Device_190', 'Office 1', 4),
-- ('Device_191', 'Office 2', 4), ('Device_192', 'Office 2', 4), ('Device_193', 'Office 2', 4), ('Device_194', 'Office 2', 4), ('Device_195', 'Office 2', 4),
-- ('Device_196', 'Office 3', 4), ('Device_197', 'Office 3', 4), ('Device_198', 'Office 3', 4), ('Device_199', 'Office 3', 4), ('Device_200', 'Office 3', 4);




-- init.sql

CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Lookup Tables
CREATE TABLE device_types (
    type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE parameters (
    param_id SERIAL PRIMARY KEY,
    param_name VARCHAR(50) NOT NULL UNIQUE,
    param_unit VARCHAR(20)
);

-- Main Tables
CREATE TABLE devices (
    device_id SERIAL PRIMARY KEY,
    device_name VARCHAR(100) NOT NULL UNIQUE,
    location VARCHAR(100),
    install_date DATE DEFAULT CURRENT_DATE,
    device_type_id INT REFERENCES device_types(type_id)
);

CREATE TABLE readings (
    time TIMESTAMPTZ NOT NULL,
    device_id INT NOT NULL,
    param_id INT NOT NULL,
    param_value DOUBLE PRECISION,
    PRIMARY KEY (time, device_id, param_id),
    FOREIGN KEY (device_id) REFERENCES devices (device_id),
    FOREIGN KEY (param_id) REFERENCES parameters (param_id)
);

SELECT create_hypertable('readings', 'time');

CREATE TABLE alerts (
    alert_id SERIAL PRIMARY KEY,
    device_id INT REFERENCES devices(device_id),
    time TIMESTAMPTZ NOT NULL,
    message VARCHAR(255),
    severity VARCHAR(20),
    acknowledged BOOLEAN DEFAULT FALSE
);

-- Pre-populate Lookup Tables
INSERT INTO device_types (type_name) VALUES ('Energy'), ('Water'), ('Weather'), ('Atmosphere');

INSERT INTO parameters (param_name, param_unit) VALUES
-- Energy (12 Parameters)
('voltage', 'V'), ('current', 'A'), ('power_consumption', 'kWh'), ('power_factor', ''), ('frequency', 'Hz'),
('phase_angle', '°'), ('reactive_power', 'kVAR'), ('apparent_power', 'kVA'), ('line_to_line_voltage', 'V'),
('line_to_neutral_voltage', 'V'), ('circuit_breaker_status', 'bool'), ('transformer_temp', '°C'),

-- Water (11 Parameters)
('water_flow_rate', 'L/min'), ('water_pressure', 'bar'), ('water_ph', ''), ('turbidity', 'NTU'),
('conductivity', 'μS/cm'), ('dissolved_oxygen', 'mg/L'), ('water_temperature', '°C'), ('chlorine_level', 'ppm'),
('valve_status', 'bool'), ('pump_speed', 'RPM'), ('reservoir_level', '%'),

-- Weather (12 Parameters)
('air_temperature', '°C'), ('humidity', '%'), ('wind_speed', 'm/s'), ('wind_direction', '°'), ('rainfall', 'mm'),
('air_pressure', 'hPa'), ('solar_radiation', 'W/m²'), ('uv_index', ''), ('dew_point', '°C'),
('cloud_cover', '%'), ('visibility', 'km'), ('lightning_detected', 'bool'),

-- Atmosphere (13 Parameters)
('co2_level', 'ppm'), ('air_quality_index', 'AQI'), ('o3_level', 'ppb'), ('no2_level', 'ppb'),
('so2_level', 'ppb'), ('co_level', 'ppm'), ('pm25_concentration', 'µg/m³'), ('pm10_concentration', 'µg/m³'),
('volatile_organic_compounds', 'ppb'), ('radon_level', 'pCi/L'), ('ambient_noise', 'dB'),
('pollen_count', 'grains/m³'), ('mold_level', 'spores/m³');


-- Pre-populate 200 Devices
INSERT INTO devices (device_name, location, device_type_id) VALUES
-- 80 Energy Devices
('Device_001', 'Factory A', 1), ('Device_002', 'Factory A', 1), ('Device_003', 'Factory A', 1), ('Device_004', 'Factory A', 1), ('Device_005', 'Factory A', 1), ('Device_006', 'Factory A', 1), ('Device_007', 'Factory A', 1), ('Device_008', 'Factory A', 1), ('Device_009', 'Factory A', 1), ('Device_010', 'Factory A', 1), ('Device_011', 'Factory A', 1), ('Device_012', 'Factory A', 1), ('Device_013', 'Factory A', 1), ('Device_014', 'Factory A', 1), ('Device_015', 'Factory A', 1), ('Device_016', 'Factory A', 1), ('Device_017', 'Factory A', 1), ('Device_018', 'Factory A', 1), ('Device_019', 'Factory A', 1), ('Device_020', 'Factory A', 1),
('Device_021', 'Factory B', 1), ('Device_022', 'Factory B', 1), ('Device_023', 'Factory B', 1), ('Device_024', 'Factory B', 1), ('Device_025', 'Factory B', 1), ('Device_026', 'Factory B', 1), ('Device_027', 'Factory B', 1), ('Device_028', 'Factory B', 1), ('Device_029', 'Factory B', 1), ('Device_030', 'Factory B', 1), ('Device_031', 'Factory B', 1), ('Device_032', 'Factory B', 1), ('Device_033', 'Factory B', 1), ('Device_034', 'Factory B', 1), ('Device_035', 'Factory B', 1), ('Device_036', 'Factory B', 1), ('Device_037', 'Factory B', 1), ('Device_038', 'Factory B', 1), ('Device_039', 'Factory B', 1), ('Device_040', 'Factory B', 1),
('Device_041', 'Warehouse X', 1), ('Device_042', 'Warehouse X', 1), ('Device_043', 'Warehouse X', 1), ('Device_044', 'Warehouse X', 1), ('Device_045', 'Warehouse X', 1), ('Device_046', 'Warehouse X', 1), ('Device_047', 'Warehouse X', 1), ('Device_048', 'Warehouse X', 1), ('Device_049', 'Warehouse X', 1), ('Device_050', 'Warehouse X', 1), ('Device_051', 'Warehouse X', 1), ('Device_052', 'Warehouse X', 1), ('Device_053', 'Warehouse X', 1), ('Device_054', 'Warehouse X', 1), ('Device_055', 'Warehouse X', 1), ('Device_056', 'Warehouse X', 1), ('Device_057', 'Warehouse X', 1), ('Device_058', 'Warehouse X', 1), ('Device_059', 'Warehouse X', 1), ('Device_060', 'Warehouse X', 1),
('Device_061', 'Warehouse Y', 1), ('Device_062', 'Warehouse Y', 1), ('Device_063', 'Warehouse Y', 1), ('Device_064', 'Warehouse Y', 1), ('Device_065', 'Warehouse Y', 1), ('Device_066', 'Warehouse Y', 1), ('Device_067', 'Warehouse Y', 1), ('Device_068', 'Warehouse Y', 1), ('Device_069', 'Warehouse Y', 1), ('Device_070', 'Warehouse Y', 1), ('Device_071', 'Warehouse Y', 1), ('Device_072', 'Warehouse Y', 1), ('Device_073', 'Warehouse Y', 1), ('Device_074', 'Warehouse Y', 1), ('Device_075', 'Warehouse Y', 1), ('Device_076', 'Warehouse Y', 1), ('Device_077', 'Warehouse Y', 1), ('Device_078', 'Warehouse Y', 1), ('Device_079', 'Warehouse Y', 1), ('Device_080', 'Warehouse Y', 1),
-- 50 Water Devices
('Device_081', 'Factory A', 2), ('Device_082', 'Factory A', 2), ('Device_083', 'Factory A', 2), ('Device_084', 'Factory A', 2), ('Device_085', 'Factory A', 2), ('Device_086', 'Factory A', 2), ('Device_087', 'Factory A', 2), ('Device_088', 'Factory A', 2), ('Device_089', 'Factory A', 2), ('Device_090', 'Factory A', 2),
('Device_091', 'Factory B', 2), ('Device_092', 'Factory B', 2), ('Device_093', 'Factory B', 2), ('Device_094', 'Factory B', 2), ('Device_095', 'Factory B', 2), ('Device_096', 'Factory B', 2), ('Device_097', 'Factory B', 2), ('Device_098', 'Factory B', 2), ('Device_099', 'Factory B', 2), ('Device_100', 'Factory B', 2), ('Device_101', 'Factory B', 2), ('Device_102', 'Factory B', 2), ('Device_103', 'Factory B', 2), ('Device_104', 'Factory B', 2), ('Device_105', 'Factory B', 2),
('Device_106', 'Warehouse X', 2), ('Device_107', 'Warehouse X', 2), ('Device_108', 'Warehouse X', 2), ('Device_109', 'Warehouse X', 2), ('Device_110', 'Warehouse X', 2), ('Device_111', 'Warehouse X', 2), ('Device_112', 'Warehouse X', 2), ('Device_113', 'Warehouse X', 2), ('Device_114', 'Warehouse X', 2), ('Device_115', 'Warehouse X', 2),
('Device_116', 'Warehouse Y', 2), ('Device_117', 'Warehouse Y', 2), ('Device_118', 'Warehouse Y', 2), ('Device_119', 'Warehouse Y', 2), ('Device_120', 'Warehouse Y', 2), ('Device_121', 'Warehouse Y', 2), ('Device_122', 'Warehouse Y', 2), ('Device_123', 'Warehouse Y', 2), ('Device_124', 'Warehouse Y', 2), ('Device_125', 'Warehouse Y', 2), ('Device_126', 'Warehouse Y', 2), ('Device_127', 'Warehouse Y', 2), ('Device_128', 'Warehouse Y', 2), ('Device_129', 'Warehouse Y', 2), ('Device_130', 'Warehouse Y', 2),
-- 35 Weather Devices
('Device_131', 'Rooftop A', 3), ('Device_132', 'Rooftop A', 3), ('Device_133', 'Rooftop A', 3), ('Device_134', 'Rooftop A', 3), ('Device_135', 'Rooftop A', 3), ('Device_136', 'Rooftop B', 3), ('Device_137', 'Rooftop B', 3), ('Device_138', 'Rooftop B', 3), ('Device_139', 'Rooftop B', 3), ('Device_140', 'Rooftop B', 3), ('Device_141', 'Rooftop X', 3), ('Device_142', 'Rooftop X', 3), ('Device_143', 'Rooftop X', 3), ('Device_144', 'Rooftop X', 3), ('Device_145', 'Rooftop X', 3), ('Device_146', 'Rooftop Y', 3), ('Device_147', 'Rooftop Y', 3), ('Device_148', 'Rooftop Y', 3), ('Device_149', 'Rooftop Y', 3), ('Device_150', 'Rooftop Y', 3), ('Device_151', 'Field 1', 3), ('Device_152', 'Field 1', 3), ('Device_153', 'Field 1', 3), ('Device_154', 'Field 1', 3), ('Device_155', 'Field 1', 3), ('Device_156', 'Field 2', 3), ('Device_157', 'Field 2', 3), ('Device_158', 'Field 2', 3), ('Device_159', 'Field 2', 3), ('Device_160', 'Field 2', 3), ('Device_161', 'Field 3', 3), ('Device_162', 'Field 3', 3), ('Device_163', 'Field 3', 3), ('Device_164', 'Field 3', 3), ('Device_165', 'Field 3', 3),
-- 35 Atmosphere Devices
('Device_166', 'Lab A', 4), ('Device_167', 'Lab A', 4), ('Device_168', 'Lab A', 4), ('Device_169', 'Lab A', 4), ('Device_170', 'Lab A', 4), ('Device_171', 'Lab B', 4), ('Device_172', 'Lab B', 4), ('Device_173', 'Lab B', 4), ('Device_174', 'Lab B', 4), ('Device_175', 'Lab B', 4), ('Device_176', 'Cleanroom X', 4), ('Device_177', 'Cleanroom X', 4), ('Device_178', 'Cleanroom X', 4), ('Device_179', 'Cleanroom X', 4), ('Device_180', 'Cleanroom X', 4), ('Device_181', 'Cleanroom Y', 4), ('Device_182', 'Cleanroom Y', 4), ('Device_183', 'Cleanroom Y', 4), ('Device_184', 'Cleanroom Y', 4), ('Device_185', 'Cleanroom Y', 4), ('Device_186', 'Office 1', 4), ('Device_187', 'Office 1', 4), ('Device_188', 'Office 1', 4), ('Device_189', 'Office 1', 4), ('Device_190', 'Office 1', 4), ('Device_191', 'Office 2', 4), ('Device_192', 'Office 2', 4), ('Device_193', 'Office 2', 4), ('Device_194', 'Office 2', 4), ('Device_195', 'Office 2', 4), ('Device_196', 'Office 3', 4), ('Device_197', 'Office 3', 4), ('Device_198', 'Office 3', 4), ('Device_199', 'Office 3', 4), ('Device_200', 'Office 3', 4);