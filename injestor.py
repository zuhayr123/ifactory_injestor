#this class should do the following
# 1: Listen to a socket connection at all times and generate interfaces based on triggers
# 2: Now save these interfaces as JSON files in proper directory structures
# 3: Now that the strctures are created, go ahead and use them to parse data received on brokers.

import socketio
import os
import json
from MQTT_Watchdog import MQTTHandler

sio = socketio.Client()
mqtt_handler = MQTTHandler("127.0.0.1", 1883)

@sio.on('connect')
def on_connect():
    print('Connected to Socket.IO server!')

@sio.on('disconnect')
def on_disconnect():
    print('Disconnected from Socket.IO server!')

@sio.on('create_device_interface')
def on_create_device_interface(data):
    print('Message received for "create_device_interface":', data)
    create_folder_and_file(data=data)
    # Assuming you also receive broker_address in the data
    broker_address = "127.0.0.1"
    port = data.get('data', {}).get('connect_at')
    topic = data.get('data', {}).get('topic', '')
    email = data.get('data', {}).get('admin', '')
    device_name = data.get('data', {}).get('device_name', 'default_device')

    print("data found on broker address " + broker_address + "port is " + port + " topic is " + topic + " email id is " + email + " device name is " + device_name)

    # # Connect to the broker if not already connected
    # if not mqtt_handler.client.is_connected():
    #     mqtt_handler.connect(broker_address, int(1883))

    # # Subscribe to the topic
    # mqtt_handler.subscribe(topic, email, device_name)

def create_folder_and_file(data):
    email = data.get('data', {}).get('admin', '')
    folder_name = email.replace('@', '_')  # Replace '@' with '_'
    
    device_name = data.get('data', {}).get('device_name', 'default_device')
    json_filename = device_name.replace(' ', '_') + ".json"  # Replace spaces with '_' and append ".json"

    # Ensure parent folder "interfaces" exists
    if not os.path.exists('interfaces'):
        os.makedirs('interfaces')

    # Complete path for the individual folder inside "interfaces"
    complete_path = os.path.join('interfaces', folder_name)

    # Ensure individual folder exists or create it
    if not os.path.exists(complete_path):
        os.makedirs(complete_path)

    # Write the entire data to the file
    with open(os.path.join(complete_path, json_filename), 'w') as f:
        json.dump(data.get('data', {}), f, indent=4)

def main():
    try:
        sio.connect('http://localhost:3000/')
        sio.wait()
    except Exception as e:
        print("Error:", e)

if __name__ == '__main__':
    main()
