""" 
Backend server for the packaging machine
Loads, creates and sends data to database and different
kafka topics

File written in pylint standard
author: Lukas Graf
"""

import time
import json
import random
import threading

import requests
import psycopg2
from kafka import KafkaConsumer, KafkaProducer
from flask import Flask, request

app = Flask(__name__)
RUNNING = False

producer = KafkaProducer(bootstrap_servers=["kafka:9092"])
TOPIC_MODEL = "decision-tree-packaging"

conn = psycopg2.connect("postgres://user:password@postgres:5432/mydb")
cursor = conn.cursor()

def data_packaging_machine(obj_id: int, params: dict) -> dict:
    """Simulates machine output"""
    time.sleep(random.randint(3, 7))
    return {
        "machine_id": 1003,
        "obj_id": obj_id,
        "package_weight (kg)" : params.get("param1"),
        "packaging_material" : params.get("param2"),
        "time_stamp" : time.time()
    }

def task(params: dict) -> None:
    """
    Produces simulated data for the packaging machine and sends it to
    kafka topics / database

    Parameters
    ----------
        params : dict
            -> Dictionary which holds the input parameters
            given in the frontend

    Returns
    -------
        None
    """
    # Create new consumer for every start stop -> Otherwise big error
    consumer = KafkaConsumer(
        "machine-assrobot-data",
        bootstrap_servers=["kafka:9092"],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id="machine-ass-robot-consumer-group"
    )

    while RUNNING:
        # Get obj_id from cnc kafka producer
        for message in consumer:

            # Exit loop cleanly if thread stops
            if not RUNNING:
                break

            data = message.value
            obj_id = data.get("obj_id")

            if obj_id:
                # Create data
                data = data_packaging_machine(
                    obj_id=obj_id,
                    params=params
                    )
                print(f"RUNNING task Packaging... with data: {data}", flush=True)

                # Send to postgres
                cursor.execute(
                    """INSERT INTO machine_packaging (machine_id, obj_id, package_weight,
                    packaging_material, time_stamp, quality_prediction)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    (data["machine_id"], data["obj_id"],
                     data["package_weight (kg)"], data["packaging_material"],
                     data["time_stamp"], "No Prediction")
                )
                conn.commit()
                print("Sent data to postgres", flush=True)

                # Send to data to kafka for decision tree layer
                producer.send(
                    topic=TOPIC_MODEL,
                    value=json.dumps(data).encode("utf-8")
                )

                # Notify frontend that machine produced a part
                requests.post("http://frontend:5000/notify/packaging", timeout=10)

    consumer.close()

@app.route('/start', methods=['POST'])
def start() -> str:
    """
    Starts a thread which begins to produce data

    Returns
    -------
        str
    """
    global RUNNING
    if not RUNNING:
        RUNNING = True
        params = request.get_json() or {}
        threading.Thread(target=task, args=(params,)).start()
        return f"Machine started Packaging with params: {params}"
    return "Machine already RUNNING Packaging"

@app.route('/stop', methods=['POST'])
def stop() -> str:
    """
    Stops the production of data

    Returns
    -------
        str
    """
    global RUNNING
    RUNNING = False
    return "Machine stopped Packaging"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
