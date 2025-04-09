import json
import time
import random
import threading

import psycopg2
from flask import Flask
from kafka import KafkaConsumer


app = Flask(__name__)

running = False

consumer = KafkaConsumer(
    "machine-cnc-data",
    bootstrap_servers=["kafka:9092"],
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',  # or 'latest' depending on your need
    enable_auto_commit=True,
    group_id="machine2-group"
)

conn = psycopg2.connect("postgres://user:password@postgres:5432/mydb")
cursor = conn.cursor()


def data_assembly_robot(obj_id: int) -> dict:
    """Simulates machine output"""
    time.sleep(random.randint(6, 14))
    return {
        "machine_id": 1002,
        "obj_id": obj_id,
        "speed_of_movement (m/s)" : random.uniform(a=0.2, b=1.0),
        "load_weight (kg)" : round(random.uniform(a=0.4, b=5.0), 2),
        "time_stamp" : time.time()
    }

def run_machine() -> None:
    global running

    while running:
        for message in consumer:
            data = message.value
            obj_id = data.get("obj_id")  # Replace with your actual key
            if obj_id:
                print(f"Received obj_id: {obj_id}")

                data = data_assembly_robot(obj_id=obj_id)
                print(f"Created data: {data}")

                # Send to postgres
                cursor.execute(
                    "INSERT INTO machine_assembly_robot (machine_id, obj_id, speed_of_movement, load_weight, time_stamp) VALUES (%s, %s, %s, %s, %s)",
                    (data["machine_id"], data["obj_id"], data["speed_of_movement (m/s)"], data["load_weight (kg)"], data["time_stamp"])
                )
                conn.commit()

@app.route("/start_machine_assembly_robot", methods=["POST"])
def start_machine_cnc():
    global running
    if not running:
        running = True
        threading.Thread(target=run_machine).start()
        print("Started machine!")

    return "Machine started", 200

@app.route("/stop_machine_assembly_robot", methods=["POST"])
def stop_machine_cnc():
    global running
    running = False
    print("Stopped machine!")
    return "Machine stopped", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
