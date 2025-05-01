""" 
Labels that the decision tree outputs for quality_prediction:
    - Good
    - Average
    - Bad

Standard value for quality_prediction:
    - No prediction
"""

import json
import random

import requests
import psycopg2
from kafka import KafkaConsumer

# Setup connection to database
conn = psycopg2.connect("postgres://user:password@postgres:5432/mydb")
cursor = conn.cursor()

# Kafka topics to listen to
topics = [
    "decision-tree-cnc",
    "decision-tree-assembly-robot",
    "decision-tree-packaging"
    ]

def prediction() -> str:
    """Simulation function for model prediction"""
    return random.choice(["Good", "Average", "Bad"])

def consume_messages() -> None:
    consumer = KafkaConsumer(
        *topics,
        bootstrap_servers=["kafka:9092"],
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id="model-consumer-group"
    )
    
    for message in  consumer:
        """Get machine id to decide what model to use 
        If decision tree or random forest we maybe only
        need 1 model (Random Forest | Decision Tree)"""
        data = message.value
        machine_id = data.get("machine_id")
        print(f"Machine id: {machine_id} and data: {data}",flush=True)
        if machine_id == 1001:
            # Start prediction process for CNC
            # Demo Prediction from future Decision Tree
            prediction_model = prediction()

            # Params from CNC Machine
            obj_id = data.get("obj_id")
            _tool_temperature = data.get("tool_temperature (C)") #Feature 1
            _spindle_speed = data.get("spindle_speed (RPM)") # Feature 2
            time_stamp = data.get("time_stamp")

            # Update table
            cursor.execute(
                """
                UPDATE machine_cnc
                SET quality_prediction=%s
                WHERE obj_id=%s AND time_stamp=%s
                """,
                (prediction_model, obj_id, time_stamp)
            )
            conn.commit()
            print(f"Updated table machine_cnc for obj {obj_id} with prediction {prediction_model}]")

            # Notify frontend that a prediction was made
            requests.post("http://frontend:5000/notify/decision_tree")

        elif machine_id == 1002:
            # Start prediction process for Assembly Robot
            # Demo Prediction from future Decision Tree
            prediction_model = prediction()

            # Params from CNC Machine
            obj_id = data.get("obj_id")
            _speed_movement = data.get("speed_of_movement (m/s)") #Feature 1
            _load_weight = data.get("load_weight (kg)") # Feature 2
            time_stamp = data.get("time_stamp")

            # Update table
            cursor.execute(
                """
                UPDATE machine_assembly_robot
                SET quality_prediction=%s
                WHERE obj_id=%s AND time_stamp=%s
                """,
                (prediction_model, obj_id, time_stamp)
            )
            conn.commit()
            print(f"Updated table machine_assembly_robot for obj {obj_id} with prediction {prediction_model}]")

            # Notify frontend that a prediction was made
            requests.post("http://frontend:5000/notify/decision_tree")

        elif machine_id == 1003:
            # Start prediction process for Packaging
            # Demo Prediction from future Decision Tree
            prediction_model = prediction()

            # Params from CNC Machine
            obj_id = data.get("obj_id")
            _package_weight = data.get("package_weight (kg)") #Feature 1
            _packaging_material = data.get("packaging_material") # Feature 2
            time_stamp = data.get("time_stamp")

            # Update table
            cursor.execute(
                """
                UPDATE machine_packaging
                SET quality_prediction=%s
                WHERE obj_id=%s AND time_stamp=%s
                """,
                (prediction_model, obj_id, time_stamp)
            )
            conn.commit()
            print(f"Updated table machine_assembly_robot for obj {obj_id} with prediction {prediction_model}]")

            # Notify frontend that a prediction was made
            requests.post("http://frontend:5000/notify/decision_tree")

        else:
            print(f"Machine ID: '{machine_id}' unknown -> Message not consumed.")


if __name__ == "__main__":
    consume_messages()
