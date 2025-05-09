CREATE TABLE IF NOT EXISTS machine_cnc (
    id SERIAL PRIMARY KEY,
    machine_id INT,
    obj_id INT,
    tool_temperature FLOAT,
    spindle_speed INT,
    quality_prediction VARCHAR(20),
    time_stamp DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS machine_assembly_robot (
    id SERIAL PRIMARY KEY,
    machine_id INT,
    obj_id INT,
    speed_of_movement FLOAT,
    load_weight FLOAT,
    quality_prediction VARCHAR(20),
    time_stamp DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS machine_packaging (
    id SERIAL PRIMARY KEY,
    machine_id INT,
    obj_id INT,
    package_weight FLOAT,
    packaging_material FLOAT,
    quality_prediction VARCHAR(20),
    time_stamp DOUBLE PRECISION
);

