# data_processor.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import paho.mqtt.client as mqtt
import json
from pymongo import MongoClient
from utils import fetch_current_useful, fetch_forecast_useful
from fwi_calculator import total_fwi
# MongoDB setup
mongo_client = MongoClient('mongodb://mongo:27017/')
db = mongo_client['weather_db']
collection = db['weather_data']

# MQTT setup
mqtt_broker = 'mqtt_broker'
mqtt_topic_data_raw = 'city/data_raw'
mqtt_topic_data_filtered = 'city/data_filtered'

client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe(mqtt_topic_data_raw)

def on_message(client, userdata, msg):
    try:
        raw_data = json.loads(msg.payload)
        city = raw_data['city']
        print(f"Received raw data for city: {city}")
        
        current_data = fetch_current_useful(raw_data['current_weather'])
        if current_data is None:
            print("Failed to process current weather data.")
            return

        forecast_data, forecast_time = fetch_forecast_useful(raw_data['forecast_data'])
        if forecast_data is None or forecast_time is None:
            print("Failed to process forecast data.")
            return
        
        fwi_current = total_fwi(current_data['temperature'], current_data['humidity'],
                                current_data['rain'], current_data['wind_speed'])

        fwi_forecast = [total_fwi(data[0], data[1], data[3], data[2]) for data in forecast_data]

        weather_data = {
            'city': city,
            'current_data': current_data,
            'forecast_data': forecast_data,
            'forecast_time': forecast_time,
            'fwi_current': fwi_current,
            'fwi_forecast': fwi_forecast
        }
        
        # Insert filtered data into MongoDB
        result = collection.insert_one(weather_data)
        print(f"Inserted filtered data for {city} into MongoDB")

        # Remove _id field before publishing
        weather_data.pop('_id', None)
        
        # Publish filtered data to MQTT
        client.publish(mqtt_topic_data_filtered, json.dumps(weather_data))
        print(f"Published filtered data for {city} to MQTT")
    except Exception as e:
        print(f"Error processing message: {e}")

client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, 1883, 60)
client.loop_forever()
