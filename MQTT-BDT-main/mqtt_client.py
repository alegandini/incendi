# mqtt_client.py
import paho.mqtt.client as mqtt
import json

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("city/data")

def on_message(client, userdata, msg):
    data = json.loads(msg.payload)
    print(f"Received message on {msg.topic}: {data}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

broker_ip = "127.19.0.2"
client.connect(broker_ip, 1883, 60)  # Assicurati che il nome del broker corrisponda a quello nel docker-compose.yml

client.loop_forever()
