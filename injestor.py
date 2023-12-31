#this class should do the following
# 1: Listen to a socket connection at all times and generate interfaces based on triggers
# 2: Now save these interfaces as JSON files in proper directory structures
# 3: Now that the strctures are created, go ahead and use them to parse data received on brokers.

import socketio
import os
import json
from mqtt_handler import MQTTHandler
import time

sio = socketio.Client()
mqtt_handler = MQTTHandler("localhost", 1883, sio)

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
    client_id = data.get('data', {}).get('client_id')
    collection_name = data.get('data', {}).get('collection_name')

    print("data found on broker address " + broker_address + "port is " + port + " topic is " + topic + " email id is " + email + " device name is " + device_name)

    # Connect to the broker if not already connected
    if not mqtt_handler.client.is_connected():
        mqtt_handler.connect(broker_address, int(1883))

    # Subscribe to the topic
    mqtt_handler.subscribe(topic, email, device_name, collection_name, client_id)

@sio.on('delete_device_interface')
def on_create_device_interface(data):
    print("data received is " + str(data))
    topic = data.get('data', {}).get('topic', '')
    email = data.get('data', {}).get('admin', '')
    device_name = data.get('data', {}).get('device_name', 'default_device')
    client_id = data.get('data', {}).get('client_id')
    status_topic = "status/" + client_id
    mqtt_handler.unsubscribe(topic)
    mqtt_handler.unsubscribe(status_topic)
    print('Device delete triggered with data as: '+ str(data) + " and topic as " + topic)
    delete_device_file(email= email, device_name= device_name)


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

def delete_device_file(email, device_name):
    # Convert email and device_name to the appropriate file path format
    folder_name = email.replace('@', '_')
    json_filename = device_name.replace(' ', '_') + ".json"
    
    # Construct the full path to the JSON file
    file_path = os.path.join('interfaces', folder_name, json_filename)
    
    # Check if the file exists, and delete if it does
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{json_filename} has been deleted.")
    else:
        print(f"{json_filename} not found.")

def main():
    max_retries = 12000 
    retry_interval = 10  # in seconds, which is 5 minutes
    
    # Loop for Socket.IO connection
    for attempt in range(max_retries):
        try:
            sio.connect('ws://ifactorybackend-env.eba-fagcpiid.us-west-2.elasticbeanstalk.com/')
            sio.wait()
            break  # exit the loop if connected successfully
        except Exception as e:
            print(f"Error connecting to Socket.IO server: {e}. Attempt {attempt + 1}/{max_retries}. Retrying in {retry_interval/60} minutes...")
            time.sleep(retry_interval)
    else:
        print("Failed to connect to Socket.IO server after 10 hours. Exiting.")

if __name__ == '__main__':
    main()
