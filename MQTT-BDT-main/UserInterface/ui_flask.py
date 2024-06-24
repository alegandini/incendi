from flask import Flask, render_template, request, jsonify
import sys
import os
import json
import yaml
import paho.mqtt.client as mqtt
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import get_alerts

app = Flask(__name__)

# MQTT setup
mqtt_broker = 'mqtt_broker'
mqtt_topic_city = 'city/select'
mqtt_topic_data_filtered = 'city/data_filtered'

client = mqtt.Client()
client.connect(mqtt_broker, 1883, 60)

city_data_response = {}

def load_json_to_dict(json_file_path):
    with open(json_file_path, mode='r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    return data

json_file_path = 'COMUNI.json'
italy_data = load_json_to_dict(json_file_path)

@app.route('/')
def index():
    regions = list(italy_data.keys())
    alerts_data = get_alerts()
    return render_template('index.html', regions=regions, alerts=alerts_data)

@app.route('/provinces/<region>')
def provinces(region):
    provinces = list(italy_data.get(region, {}).keys())
    return jsonify(provinces)

@app.route('/municipalities/<region>/<province>')
def municipalities(region, province):
    province_data = italy_data.get(region, {}).get(province, [])
    municipalities_names = sorted({city_info['nome'] for city_info in province_data})
    return jsonify(municipalities_names)

@app.route('/city-data', methods=['POST'])
def city_data():
    global city_data_response
    city = request.form.get('municipality')
    client.publish(mqtt_topic_city, city)
    print(f"Published city {city} to MQTT")

    # Attendi la risposta dal topic MQTT
    start_time = time.time()
    timeout = 15  # Aumenta il timeout a 15 secondi
    while city not in city_data_response:
        if time.time() - start_time > timeout:
            return jsonify({"message": "Timeout waiting for city data", "city": city})

    data = city_data_response.pop(city)
    print(f"Received data for city {city}: {data}")
    return render_template('city_data.html', city=city, current_data=data['current_data'], 
                           forecast_data=data['forecast_data'], forecast_time=data['forecast_time'],
                           fwi_current=data['fwi_current'], fwi_forecast=data['fwi_forecast'])

# MQTT callback to receive data
def on_message(client, userdata, msg):
    global city_data_response
    data = json.loads(msg.payload)
    city_data_response[data['city']] = data
    print(f"Received message on {msg.topic}: {data}")

client.on_message = on_message
client.subscribe(mqtt_topic_data_filtered)
client.loop_start()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
