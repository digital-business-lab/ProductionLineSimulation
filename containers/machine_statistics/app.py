import random
import time
from threading import Thread

import psycopg2
from flask import Flask, jsonify, render_template


app = Flask(__name__)

conn = psycopg2.connect("postgres://user:password@postgres:5432/mydb")
cursor = conn.cursor()

# Simulated data structure
data_store = {
    "machine_cnc": [],
    "machine_assembly_robot": [],
    "machine_packaging": []
}

"""
SELECT tool_temperature, spindle_speed, time_stamp 
FROM machine_cnc
ORDER BY obj_id DESC
LIMIT 30
"""
def get_data(table_name: str) -> str:
    query_string: str = ""

    match table_name:
        case "machine_cnc":
            query_string = """
                        SELECT tool_temperature, spindle_speed, time_stamp 
                        FROM machine_cnc
                        ORDER BY obj_id ASC
                        LIMIT 30
                        """
        
        case "machine_assembly_robot":
            query_string = """
                        SELECT speed_of_movement, load_weight, time_stamp 
                        FROM machine_assembly_robot
                        ORDER BY obj_id ASC
                        LIMIT 30
                        """
            
        case "machine_packaging":
            query_string = """
                        SELECT package_weight, packaging_material, time_stamp 
                        FROM machine_packaging
                        ORDER BY obj_id ASC
                        LIMIT 30
                        """
            
    return query_string
    
def update_data():
    while True:
        for key in data_store:
            query: str = get_data(key)
            cursor.execute(query)
            results: list = cursor.fetchall() # List of tuples

            vis_list = []
            for m1, m2, ts in results:
                vis_list.append({
                    "timestamp": ts,
                    "value1": m1,
                    "value2": m2
                })
            
            data_store[key] = vis_list

            # if len(data_store[key]) > 30:
            #     data_store[key].pop(0)
        time.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data/<section>')
def get_section_data(section):
    return jsonify(data_store.get(section, []))


if __name__ == "__main__":
    Thread(target=update_data, daemon=True).start()
    app.run(host="0.0.0.0", port=5050)
