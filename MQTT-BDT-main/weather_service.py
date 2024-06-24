# weather_service.py
import paho.mqtt.client as mqtt
import requests
import json
from pymongo import MongoClient
import yaml
from utils import fetch_forecast_useful
from fwi_calculator import total_fwi

print("Starting weather_service...")

# MongoDB setup
mongo_client = MongoClient('mongodb://mongo:27017/')
db = mongo_client['weather_db']
collection = db['weather_data']
print("Connected to MongoDB")

# MQTT setup
mqtt_broker = 'mqtt_broker'
mqtt_topic_city = 'city/select'
mqtt_topic_data = 'city/data'

client = mqtt.Client()

def fetch_current_useful(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        current_data = {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'rain': data.get('rain', {}).get('1h', 0)
        }
        return current_data
    else:
        print(f"Failed to fetch current weather data for {city}. Response: {response.text}")
        return None

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe(mqtt_topic_city)

def on_message(client, userdata, msg):
    city = msg.payload.decode()
    print(f"Received city: {city}")
    with open("config.yaml", "r") as f:
        config_data = yaml.safe_load(f)
    api_key = config_data["API"]["api"]
    
    current_data = fetch_current_useful(api_key, city)
    if not current_data:
        print(f"Failed to fetch current data for {city}")
        return
    
    print(f"Current data: {current_data}")
    forecast_data, forecast_time = fetch_forecast_useful(api_key, city)
    if not forecast_data:
        print(f"Failed to fetch forecast data for {city}")
        return

    print(f"Forecast data: {forecast_data}")

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
    
    # Insert data into MongoDB and remove the ObjectId
    result = collection.insert_one(weather_data)
    print(f"Inserted data for {city} into MongoDB")

    # Remove the _id field before publishing
    weather_data.pop('_id', None)

    client.publish(mqtt_topic_data, json.dumps(weather_data))
    print(f"Published data for {city} to MQTT")

client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, 1883, 60)
client.loop_forever()
