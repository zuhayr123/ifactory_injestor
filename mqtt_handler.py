import json
import paho.mqtt.client as mqtt
import os

class MQTTHandler:
    def __init__(self, broker_address, port):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        # Connect to the MQTT broker immediately
        self.connect(broker_address, port)

        # Subscribe to topics from the existing interfaces
        self.initial_subscribe()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT with result code {str(rc)}")

    def on_message(self, client, userdata, msg):
        payload = msg.payload.decode('utf-8')
        interface_file_path = self.get_interface_file_path(userdata)
        print("path found was " + interface_file_path + " and payload is " + payload)

        if os.path.exists(interface_file_path):
            with open(interface_file_path, 'r') as f:
                data = json.load(f)
                interface_str = data["interface"]
                interface = json.loads(interface_str)  # convert the string representation to a dictionary
                print("interface data is:", interface)
                
                try:
                    parsed_data = json.loads(payload)
                    for key in interface:
                        if key not in parsed_data:
                            print(f"Key {key} from interface not found in received data.")
                except json.JSONDecodeError:
                    print("Received data is not valid JSON.")
        else:
            print(f"No interface found for {userdata['device_name']}")

    def get_interface_file_path(self, data):
        email = data.get('email', '')
        folder_name = email.replace('@', '_')  # Replace '@' with '_'
        
        device_name = data.get('device_name', 'default_device')
        json_filename = device_name.replace(' ', '_') + ".json"  # Replace spaces with '_' and append ".json"

        # Construct the path to the interface file
        complete_path = os.path.join('interfaces', folder_name, json_filename)

        return complete_path

    def connect(self, broker_address, port):
        self.client.connect(broker_address, port)
        self.client.loop_start()

    def subscribe(self, topic, email, device_name):
        self.client.user_data_set({
            "email": email,
            "device_name": device_name
        })
        self.client.subscribe(topic)
    
    def unsubscribe(self, topic):
        self.client.unsubscribe(topic)
    
    def initial_subscribe(self):
        print("Initial subscribe was called")
        for root, _, files in os.walk('interfaces'):
            for file_name in files:
                if file_name.endswith('.json'):
                    file_path = os.path.join(root, file_name)
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        topic = data.get("topic")
                        if topic:
                            # Extract email and device name from file path
                            _, email_folder, device_name_only = file_path.split(os.sep)
                            email = email_folder.replace('_', '@')
                            device_name = device_name_only.rsplit('.', 1)[0].replace('_', ' ')
                            print("trying to subscribe to  " + topic)
                            self.subscribe(topic, email, device_name)
