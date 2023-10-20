import json
import paho.mqtt.client as mqtt
import os

class MQTTHandler:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT with result code {str(rc)}")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        interface_file_path = f'interfaces/{userdata["email"]}/{userdata["device_name"]}.json'

        if os.path.exists(interface_file_path):
            with open(interface_file_path, 'r') as f:
                interface = json.load(f)
                try:
                    parsed_data = json.loads(payload)
                    for key in interface:
                        if key not in parsed_data:
                            print(f"Key {key} from interface not found in received data.")
                except json.JSONDecodeError:
                    print("Received data is not valid JSON.")
        else:
            print(f"No interface found for {userdata['device_name']}")

    def connect(self, broker_address, port):
        self.client.connect(broker_address, port)
        self.client.loop_start()

    def subscribe(self, topic, email, device_name):
        self.client.user_data_set({
            "email": email,
            "device_name": device_name
        })
        self.client.subscribe(topic)
