from flask import Flask, jsonify, render_template
from threading import Thread
import time
import random

app = Flask(__name__)

# Simulated data structure
data_store = {
    "cnc": [],
    "ar": [],
    "pack": []
}

def update_data():
    while True:
        timestamp = time.time()
        for key in data_store:
            data_store[key].append({
                "timestamp": timestamp,
                "value1": random.randint(0, 100),
                "value2": random.randint(0, 100)
            })
            if len(data_store[key]) > 20:
                data_store[key].pop(0)
        time.sleep(30)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data/<section>')
def get_section_data(section):
    return jsonify(data_store.get(section, []))


if __name__ == "__main__":
    Thread(target=update_data, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=True)
