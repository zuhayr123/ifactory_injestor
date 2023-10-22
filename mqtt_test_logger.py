import paho.mqtt.client as mqtt

device_id = "GWr_ejBDnlvKSHuVbzTVL2BIonRcllQd-vZS7k5kEwk"
# Define the LWT message
LWT_TOPIC = "status/" + device_id
LWT_PAYLOAD = "offline"
BIRTH_PAYLOAD = "online"

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Publish the birth message
    client.publish(LWT_TOPIC, BIRTH_PAYLOAD, qos=1, retain=True)

client = mqtt.Client(client_id=device_id)
client.on_connect = on_connect  # Assign the on_connect callback function
client.will_set(LWT_TOPIC, LWT_PAYLOAD, qos=1, retain=True)
client.connect("127.0.0.1", 1883)

# Start the network loop
client.loop_forever()
