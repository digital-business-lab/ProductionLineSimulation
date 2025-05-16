""" 
Backend server for the cnc machine
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
from kafka import KafkaProducer
from flask import Flask, request

app = Flask(__name__)
RUNNING = False

# Producer for Machine Assembly Robot
producer = KafkaProducer(bootstrap_servers=["kafka:9092"])
TOPIC_MACHINE = "machine-cnc-data"
TOPIC_MODEL = "decision-tree-cnc"

conn = psycopg2.connect("postgres://user:password@postgres:5432/mydb")
cursor = conn.cursor()

def data_cnc_machine(obj_id: int, params: dict) -> dict:
    """Simulates machine output"""
    time.sleep(random.randint(3, 8))
    return {
        "machine_id": 1001,
        "obj_id": obj_id,
        "tool_temperature (C)": params.get("param1"),
        "spindle_speed (RPM)": params.get("param2"),
        "time_stamp": time.time()
    }

def task(params: dict) -> None:
    """
    Produces simulated data for the cnc machine and sends it to
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
    # Counter for obj_id
    obj_id: int = 0

    # Generate data while RUNNING
    while RUNNING:
        # Create data
        data = data_cnc_machine(
            obj_id=obj_id,
            params=params
        )
        print(f"RUNNING task CNC... with data: {data}", flush=True)

        # Send to kafka for machine assembly robot
        producer.send(
            topic=TOPIC_MACHINE,
            value=json.dumps(data).encode("utf-8")
        )
        print(f"Sent data to kafka topic: {TOPIC_MACHINE}", flush=True)

        # Send to postgres
        cursor.execute(
            """INSERT INTO machine_cnc (machine_id, obj_id, tool_temperature,
            spindle_speed, time_stamp, quality_prediction)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (data["machine_id"], data["obj_id"], data["tool_temperature (C)"],
             data["spindle_speed (RPM)"], data["time_stamp"], "No Prediction")
        )
        conn.commit()
        print("Sent data to postgres", flush=True)

        # Send to data to kafka for decision tree layer
        producer.send(
            topic=TOPIC_MODEL,
            value=json.dumps(data).encode("utf-8")
        )

        # Notify frontend that machine produced a part
        # requests.post("http://frontend:5000/notify/cnc", timeout=10)

        obj_id += 1

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
        return f"Machine started CNC with params: {params}"
    return "Machine already RUNNING CNC"

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
    return "Machine stopped CNC"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
