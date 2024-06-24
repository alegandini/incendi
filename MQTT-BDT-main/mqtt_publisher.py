import paho.mqtt.client as mqtt
import json

# Configurazione del client MQTT
broker_address = "mqtt_broker"
port = 1883
topic = "city/data"

# Creazione del client MQTT
client = mqtt.Client()

# Connessione al broker
client.connect(broker_address, port=port)

# Funzione per inviare un messaggio
def publish_message(message):
    client.publish(topic, json.dumps(message))

# Esempio di messaggio da inviare
message = {
    "city": "Milan",
    "temperature": 22.5,
    "humidity": 60
}

# Invio del messaggio
publish_message(message)
print("Messaggio inviato al topic:", topic)

# Disconnessione dal broker
client.disconnect()
