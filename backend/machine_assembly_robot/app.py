import time
import json
import random
import threading

import requests
import psycopg2
from kafka import KafkaConsumer, KafkaProducer
from flask import Flask, request

app = Flask(__name__)
running = False
params = {}

producer = KafkaProducer(bootstrap_servers=["kafka:9092"])
topic = "machine-assrobot-data"

conn = psycopg2.connect("postgres://user:password@postgres:5432/mydb")
cursor = conn.cursor()

def data_assembly_robot(obj_id: int, params: dict) -> dict:
    """Simulates machine output"""
    time.sleep(random.randint(6, 14))
    return {
        "machine_id": 1002,
        "obj_id": obj_id,
        "speed_of_movement (m/s)" : params.get("param1"),
        "load_weight (kg)" : params.get("param2"),
        "time_stamp" : time.time()
    }

def task(params):
    # Create new consumer for every start stop -> Otherwise big error
    consumer = KafkaConsumer(
        "machine-cnc-data",
        bootstrap_servers=["kafka:9092"],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
    )

    while running:
        # Get obj_id from cnc kafka producer
        for message in consumer:

            # Exit loop cleanly if thread stops
            if not running:
                break

            data = message.value
            obj_id = data.get("obj_id")

            if obj_id:
                # Create data
                data = data_assembly_robot(
                    obj_id=obj_id,
                    params=params
                    )
                print(f"Running task AR... with data: {data}", flush=True)

                # Send to kafka
                producer.send(
                    topic=topic,
                    value=json.dumps(data).encode("utf-8")
                )
                print(f"Sent data to kafka topic: {topic}", flush=True)

                # Send to postgres
                cursor.execute(
                    "INSERT INTO machine_assembly_robot (machine_id, obj_id, speed_of_movement, load_weight, time_stamp) VALUES (%s, %s, %s, %s, %s)",
                    (data["machine_id"], data["obj_id"], data["speed_of_movement (m/s)"], data["load_weight (kg)"], data["time_stamp"])
                )
                conn.commit()
                print("Sent data to postgres", flush=True)

                # Notify frontend that machine produced a part
                requests.post("http://frontend:5000/notify/assembly_robot")

    consumer.close()

@app.route('/start', methods=['POST'])
def start():
    global running, params
    if not running:
        running = True
        params = request.get_json() or {}
        threading.Thread(target=task, args=(params,)).start()
        return f"Machine started AR with params: {params}"
    return "Machine already running AR"

@app.route('/stop', methods=['POST'])
def stop():
    global running
    running = False
    return "Machine stopped AR"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)  # For B, use 5002
