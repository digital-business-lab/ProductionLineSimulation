""" 
File dealing with all the frontend function
File written in pylint standard

author: Lukas Graf
"""

import requests
from flask_socketio import SocketIO
from flask import Flask, render_template, request

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

MACHINE_CNC = 'http://machine_cnc:5001'
MACHINE_ASSEMBLY_ROBOT = 'http://machine_assembly_robot:5002'
MACHINE_PACKAGING = 'http://machine_packaging:5003'

@app.route('/')
def index():
    """Renders standard template for frontend"""
    return render_template('index.html')

@app.route('/notify/<machine>', methods=['POST'])
def notify(machine):
    """
    Function that writes to socketio when it get called
    Used to make container blink when sending data

    Parameters
    ----------
        machine
            -> The machine which sends data

    Returns
    -------
        Any
    """
    socketio.emit('machine_activity', {'machine': machine})
    return "Notification sent", 200

@app.route('/start/<machine>', methods=['POST'])
def start_machine(machine: str) -> str:
    """ 
    Makes backend call to desired machine when corresponding start
    button is pressed in the frontend

    Parameters
    ----------
        machine : str
            -> The machine which is called

    Returns
    -------
        str
    """
    if machine == "cnc":
        target = MACHINE_CNC
    elif machine == "assembly_robot":
        target = MACHINE_ASSEMBLY_ROBOT
    elif machine == "packaging":
        target = MACHINE_PACKAGING
    else:
        raise ValueError(f"No endpoint for {machine}")

    data = request.get_json()
    r = requests.post(f'{target}/start', json=data, timeout=10)
    return r.text

@app.route('/stop/<machine>', methods=['POST'])
def stop_machine(machine) -> str:
    """ 
    Makes backend call to desired machine when corresponding stop
    button is pressed in the frontend

    Parameters
    ----------
        machine : str
            -> The machine which is called

    Returns
    -------
        str
    """
    if machine == "cnc":
        target = MACHINE_CNC
    elif machine == "assembly_robot":
        target = MACHINE_ASSEMBLY_ROBOT
    elif machine == "packaging":
        target = MACHINE_PACKAGING
    else:
        raise ValueError(f"No endpoint for {machine}")

    r = requests.post(f'{target}/stop', timeout=10)
    return r.text

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
