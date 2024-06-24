# mqtt_debug.py
import paho.mqtt.client as mqtt

mqtt_broker = 'mqtt_broker'
mqtt_topic = '#'

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(mqtt_topic)

def on_message(client, userdata, msg):
    print(f"Received message on {msg.topic}: {msg.payload.decode()}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, 1883, 60)
client.loop_forever()

