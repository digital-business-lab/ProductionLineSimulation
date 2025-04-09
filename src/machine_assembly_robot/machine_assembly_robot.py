import time
import random
import threading

import psycopg2
from flask import Flask


app = Flask(__name__)

running = False

# producer = KafkaProducer(bootstrap_servers=["kafka:9092"])
# topic = "machine-cnc-data"

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
    obj_id = 0

    while running:
        data = data_assembly_robot(obj_id=obj_id)
        print(f"Created data: {data}")

        # Send to kafka -> Not used yet
        # producer.send(
        #     topic=topic,
        #     value=json.dumps(data).encode("utf-8")
        #     )
        # print("Kafka sent data")

        # Send to postgres
        cursor.execute(
            "INSERT INTO machine_assembly_robot (machine_id, obj_id, speed_of_movement, load_weight, time_stamp) VALUES (%s, %s, %s, %s, %s)",
            (data["machine_id"], data["obj_id"], data["speed_of_movement (m/s)"], data["load_weight (kg)"], data["time_stamp"])
        )
        conn.commit()

        obj_id += 1

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
