# data_fetcher.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paho.mqtt.client as mqtt
import requests
import json
from pymongo import MongoClient
import yaml

# MongoDB setup
mongo_client = MongoClient('mongodb://mongo:27017/')
db = mongo_client['data_db']
collection = db['data_row']

# MQTT setup
mqtt_broker = 'mqtt_broker'
mqtt_topic_city = 'city/select'
mqtt_topic_data_raw = 'city/data_raw'

client = mqtt.Client()

def fetch_current_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to fetch current weather data for {city}. Response: {response.text}")
        return None

def fetch_forecast(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Failed to fetch forecast data for {city}. Response: {response.text}")
        return None

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(mqtt_topic_city)

def on_message(client, userdata, msg):
    try:
        city = msg.payload.decode()
        print(f"Received city: {city}")
        with open("config.yaml", "r") as f:
            config_data = yaml.safe_load(f)
        api_key = config_data["API"]["api"]
        
        current_weather = fetch_current_weather(api_key, city)
        forecast_data = fetch_forecast(api_key, city)

        if current_weather and forecast_data:
            raw_data = {
                'city': city,
                'current_weather': current_weather,
                'forecast_data': forecast_data
            }
            
            # Insert raw data into MongoDB
            result = collection.insert_one(raw_data)
            print(f"Inserted raw data for {city} into MongoDB")
            
            # Remove the _id field before publishing
            raw_data.pop('_id', None)
            
            # Publish raw data to MQTT
            client.publish(mqtt_topic_data_raw, json.dumps(raw_data))
            print(f"Published raw data for {city} to MQTT")
        else:
            print(f"Failed to fetch data for {city}")

    except Exception as e:
        print(f"Error processing message for city {city}: {e}")

client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, 1883, 60)
client.loop_forever()
