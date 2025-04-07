CREATE TABLE IF NOT EXISTS machine_cnc (
    id SERIAL PRIMARY KEY,
    machine_id INT,
    obj_id INT,
    tool_temperature FLOAT,
    spindle_speed INT,
    time_stamp DOUBLE PRECISION
);
