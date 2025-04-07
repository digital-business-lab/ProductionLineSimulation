import time
import json
import random
import threading

import psycopg2
from flask import Flask
# from kafka import KafkaProducer


app = Flask(__name__)

running = False

# producer = KafkaProducer(bootstrap_servers=["kafka:9092"])
# topic = "machine-cnc-data"

conn = psycopg2.connect("postgres://user:password@postgres:5432/mydb")
cursor = conn.cursor()

def data_cnc_machine(obj_id: int) -> dict:
    """Simulates machine output"""
    time.sleep(random.randint(3, 8))
    return {
        "machine_id": 1001,
        "obj_id": obj_id,
        "tool_temperature (C)": random.uniform(18.0, 23.0),
        "spindle_speed (RPM)": random.randint(400, 1800),
        "time_stamp": time.time()
    }

def run_machine() -> None:
    global running
    obj_id = 0

    while running:
        data = data_cnc_machine(obj_id=obj_id)
        print(f"Created data: {data}")

        # Send to kafka -> Not used yet
        # producer.send(
        #     topic=topic,
        #     value=json.dumps(data).encode("utf-8")
        #     )
        # print("Kafka sent data")

        # Send to postgres
        cursor.execute(
            "INSERT INTO machine_cnc (machine_id, obj_id, tool_temperature, spindle_speed, time_stamp) VALUES (%s, %s, %s, %s, %s)",
            (data["machine_id"], data["obj_id"], data["tool_temperature (C)"], data["spindle_speed (RPM)"], data["time_stamp"])
        )
        conn.commit()

        obj_id += 1
        
@app.route("/start_machine_cnc", methods=["POST"])
def start_machine_cnc():
    global running
    if not running:
        running = True
        threading.Thread(target=run_machine).start()
        print("Started machine!")

    return "Machine started", 200

@app.route("/stop_machine_cnc", methods=["POST"])
def stop_machine_cnc():
    global running
    running = False
    print("Stopped machine!")
    return "Machine stopped", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
