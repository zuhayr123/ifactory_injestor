import os
import sys
import socketio
import random
import requests
from datetime import datetime
import uuid

# Constants
SOCKETIO_URL = "http://192.168.1.5:3000"
API_URL = "http://192.168.1.5:3000/register_broker"
TOKEN = "EMPTY_TOKEN"  # Replace with your token
ACTUAL_TOKEN = ""

sio = socketio.Client()

def generate_unique_clientID():
    return str(uuid.uuid4())


@sio.event
def connect():
    print("Connected to Socket.IO server!")

@sio.on('delete_broker')
def delete_broker(token):
    TOKEN = token.get('client_id')
    stop_broker_by_clientID(TOKEN)

@sio.on('create_broker')
def new_client(token):
    TOKEN = token.get('client_id')
    clientID = generate_unique_clientID()
    print('Create Broker Was Called')
    port = generate_random_port()
    create_pid_directory()
    create_mosquitto_config(clientID, port)
    create_supervisor_config(clientID, port)
    start_broker(clientID)

    # Send data to API
    headers = {
        "x-access-token": TOKEN
    }
    data = {
        "port_number": port,
        "timestamp": datetime.now().isoformat()
    }
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code != 200:
        print(f"Failed to save data for clientID {TOKEN}. API Response: {response.text}")


def generate_random_port():
    # Assuming the valid range for your ports is between 10000 and 60000
    # Adjust as necessary
    return random.randint(10000, 60000)


# ... [Your previous functions: create_mosquitto_config, create_supervisor_config, create_pid_directory, start_broker] ...

def create_mosquitto_config(clientID, port):
    print('Creating mosquitto config file')
    config_content = f"""
pid_file /var/run/mosquitto/mosquitto.{clientID}.pid
listener {port}
allow_anonymous true
"""

    with open(f"/etc/mosquitto/conf.d/{clientID}.conf", "w") as f:
        f.write(config_content)

def create_supervisor_config(clientID, port):
    print('creating mosquitto supervisor config')
    config_content = f"""
[program:mosquitto_{clientID}]
command=mosquitto -c /etc/mosquitto/conf.d/{clientID}.conf
stdout_logfile=/var/log/supervisor/mosquitto_{clientID}.out.log
stderr_logfile=/var/log/supervisor/mosquitto_{clientID}.err.log
autostart=true
autorestart=true
redirect_stderr=true
"""

    with open(f"/etc/supervisor/conf.d/mosquitto_{clientID}.conf", "w") as f:
        f.write(config_content)

def create_pid_directory():
    print('creating mosquitto pid directory')
    if not os.path.exists("/var/run/mosquitto"):
        os.system("sudo mkdir /var/run/mosquitto/")
        os.system("sudo chown mosquitto: /var/run/mosquitto/")

def start_broker(clientID):
    print('Starting broker')
    os.system(f"sudo supervisorctl reread")
    os.system(f"sudo supervisorctl add mosquitto_{clientID}")
    os.system(f"sudo supervisorctl start mosquitto_{clientID}")

def stop_broker_by_clientID(clientID):
    # Stop the associated Supervisor process
    os.system(f"sudo supervisorctl stop mosquitto_{clientID}")
    
    # Remove the Supervisor configuration for the broker
    os.remove(f"/etc/supervisor/conf.d/mosquitto_{clientID}.conf")
    
    # Remove the Mosquitto configuration for the broker
    os.remove(f"/etc/mosquitto/conf.d/{clientID}.conf")
    print("Device removed " + clientID)



def get_clientID_by_port(port):
    # This function checks the Mosquitto configurations to find the clientID associated with a given port.
    # It's a simple approach based on scanning the configuration files; adjust as needed.
    
    conf_dir = "/etc/mosquitto/conf.d/"
    for conf_file in os.listdir(conf_dir):
        with open(os.path.join(conf_dir, conf_file), 'r') as f:
            content = f.read()
            if f"listener {port}" in content:
                # Return the clientID based on the file name, assuming it's formatted as clientID.conf
                return conf_file.replace(".conf", "")
    return None


if __name__ == "__main__":
    sio.connect(SOCKETIO_URL)
    sio.wait()
