# dask_processor.py
import json
from dask.distributed import Client
import paho.mqtt.client as mqtt
from fwi_calculator import total_fwi

# Connect to Dask scheduler
client = Client('tcp://dask_scheduler:8786')

def process_weather_data(data):
    temp = data["main"]["temp"]
    hum = data["main"]["humidity"]
    wind = data["wind"]["speed"]
    rain = data["rain"].get("1h", 0)
    
    fwi_value, fwi_level = total_fwi(temp, hum, rain, wind)
    
    # Append FWI to the data
    data["fwi"] = fwi_value
    data["fwi_level"] = fwi_level
    
    return data

def on_connect(mqtt_client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    mqtt_client.subscribe("weather_data")

def on_message(mqtt_client, userdata, msg):
    data = json.loads(msg.payload)
    future = client.submit(process_weather_data, data)
    result = future.result()
    print(f"Processed data: {result}")

mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

broker_ip = "172.20.0.2"  # Assicurati di utilizzare l'indirizzo IP corretto
client.connect(broker_ip, 1883, 60) # Assumes 'mqtt_broker' is the service name in docker-compose

client = Client(n_workers=4) 
dask_client = Client('tcp://dask_scheduler:8786')
mqtt_client.loop_forever()
