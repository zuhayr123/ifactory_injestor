import json
import paho.mqtt.client as mqtt
import os
import time
import socketio

class MQTTHandler:
    def __init__(self, broker_address, port, socketio_client):
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.sio = socketio_client

        self.topic_map = {}

        # Connect to the MQTT broker immediately
        self.connect(broker_address, port)

        # Subscribe to topics from the existing interfaces
        self.initial_subscribe()

    def on_connect(self, client, userdata, flags, rc):
        print(f"Connected to MQTT with result code {str(rc)}")

    def on_message(self, client, userdata, msg):
        if msg.topic.startswith("status/"):
            device_id = msg.topic.split("/")[-1]
            status = msg.payload.decode("utf-8")
            print(f"Device {device_id} is {status}")
            current_timestamp = int(time.time())
            
            # Emit the status on socketio
            event_data = {
                "device_id": device_id,
                "status": status,
                "timestamp": current_timestamp  # include timestamp in the emitted data
            }
            try:
                self.sio.emit('device_status', event_data)
            except socketio.exceptions.BadNamespaceError as e:
                print("Error emitting event:")
        else:
            payload = msg.payload.decode('utf-8')
            topic_data = self.topic_map.get(msg.topic, {})
            interface_file_path = self.get_interface_file_path(topic_data)
            print("path found was " + interface_file_path + " and payload is " + payload)

            if os.path.exists(interface_file_path):
                with open(interface_file_path, 'r') as f:
                    data = json.load(f)
                    interface_str = data["interface"]
                    interface = json.loads(interface_str)  # convert the string representation to a dictionary
                    print("interface data is:", interface)
                    
                    try:
                        parsed_data = json.loads(payload)
                        if all(key in parsed_data for key in interface):
                            # All keys in interface are present in parsed_data
                            parsed_data["timestamp"] = str(int(time.time()))
                            event_data = {
                                "_id": topic_data.get('device_id', ''),
                                "timestamp": str(int(time.time())),  # assuming you want to send the current timestamp
                                "interface": json.dumps(parsed_data),
                                "collection_name": topic_data.get('collection_name', '')
                            }
                            self.sio.emit('device_data', event_data)
                        else:
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

        max_retries = 12000  # 120 attempts * 5 minutes each = 10 hours
        retry_interval = 10  # in seconds, which is 5 minutes
        
        # Loop for MQTT broker connection
        for attempt in range(max_retries):
            try:
                self.client.connect(broker_address, port)
                self.client.loop_start()
                break  # exit the loop if connected successfully
            except Exception as e:
                print(f"Error connecting to MQTT broker: {e}. Attempt {attempt + 1}/{max_retries}. Retrying in {retry_interval/60} minutes...")
                time.sleep(retry_interval)
        else:
            print("Failed to connect to MQTT broker after 10 hours. Exiting.")

    def subscribe(self, topic, email, device_name, collection_name, client_id):
        status_topic = "status/" + client_id
        self.client.subscribe(status_topic)
        self.topic_map[topic] = {
            "email": email,
            "device_name": device_name,
            "collection_name": collection_name,
            "client_id": client_id
        }
        
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
                        device_id = data["client_id"]
                        topic = data.get("topic")
                        if topic:
                            # Extract email and device name from file path
                            _, email_folder, device_name_only = file_path.split(os.sep)
                            email = email_folder.replace('_', '@')
                            device_name = device_name_only.rsplit('.', 1)[0].replace('_', ' ')
                            print("trying to subscribe to  " + topic)
                            collection_name = data.get("collection_name")
                            collection_name = collection_name.lower()
                            print("collection_name is " + collection_name)
                            self.subscribe(topic, email, device_name, collection_name, device_id)
                            # self.client.subscribe(status_topic)
