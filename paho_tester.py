import paho.mqtt.client as mqtt

# Callbacks
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    
    # Subscribing to the wildcard topic
    client.subscribe("#")

def on_message(client, userdata, msg):
    print(f"Topic: {msg.topic} - Message: {msg.payload.decode()}")

# Set up the MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
broker_address = "127.0.0.1"  # or replace with your broker's IP address
broker_port = 1883

client.connect(broker_address, broker_port, 60)

# Blocking call to process network traffic, dispatches callbacks, etc.
client.loop_forever()
