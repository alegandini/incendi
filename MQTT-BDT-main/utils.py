import requests
from datetime import datetime, timedelta
from fwi_calculator import total_fwi
import yaml
import argparse
import json

def fetch_current_useful(current_weather):
    temp = current_weather['main']['temp']  # °C
    hum = current_weather['main']['humidity']  # %
    win = current_weather['wind']['speed']  # m/s
    try:
        rai = current_weather['rain']['1h']  # mm
    except KeyError:
        rai = 0
    
    return {
        'temperature': temp,
        'humidity': hum,
        'wind_speed': win,
        'rain': rai
    }

def fetch_forecast_useful(forecast_data):
    forecast_data_filtered = []
    forecast_time = []
    for forecast in forecast_data['list']:
        tmp = []
        tmp.append(forecast['main']['temp'])  # °C
        tmp.append(forecast['main']['humidity'])  # %
        tmp.append(forecast['wind']['speed'])  # m/s
        try:
            tmp.append(round(forecast['rain']['3h'] / 3, 2))  # divided by 3 because the rain is reported in 3h
        except KeyError:
            tmp.append(0)  # °C
        forecast_data_filtered.append(tmp)
        forecast_time.append(forecast['dt_txt'])
    return forecast_data_filtered, forecast_time

def get_alerts():
    alerts = []
    with open('synthetic_weather_data.json', 'r', encoding='utf-8') as file:
        synthetic_data = json.load(file)
    for city_data in synthetic_data:
        weather = city_data["main"]
        temp = weather["temp"]
        hum = weather["humidity"]
        rain = city_data["rain"]["1h"] if "rain" in city_data and "1h" in city_data["rain"] else 0
        wind_speed = city_data["wind"]["speed"]

        fwi_value, fwi_level = total_fwi(temp, hum, rain, wind_speed)
        if fwi_level in ["Extreme", "Very-High", "High"]:
            alerts.append({
                "name": city_data["name"],
                "fwi_level": fwi_level
            })
    # Ordina le città per livello di allerta decrescente
    alerts.sort(key=lambda x: ["Extreme", "Very-High", "High", "Moderate"].index(x["fwi_level"]))
    return alerts


'''
def main(args):

    with open(args.config, "r") as f:
        config = yaml.safe_load(f)
    
    api_key =  config["API"]["api"]
    city = input("Enter city name: ")
    
    #current_weather_data = fetch_current_weather(api_key, city)
    #forecast_data = fetch_forecast(api_key, city)
    
    print(fetch_current_useful(api_key, city))
    print(fetch_forecast_useful(api_key, city))

    current_data=fetch_current_useful(api_key, city)
    temperature, humidity, wind_speed, rain = current_data
    fwi.total_fwi(temperature,humidity, rain, wind_speed)
    
    #display_current_weather(current_weather_data)
    #display_forecast(forecast_data)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser("")
    parser.add_argument("--config", default="config.yaml", type=str, help="Path to the configuration file")
    parser.add_argument("--run_name", required=False, type=str, help="Name of the run")
    args = parser.parse_args()
    main(args)

# TO RUN python prova.py --config config.yaml


# Fetch all data for the current weather
def fetch_current_weather(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to fetch current weather data.")
        return None

# Fetch all data for the forecast of the next 5 days, in sequence of 3h
def fetch_forecast(api_key, city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to fetch forecast data.")
        return None

# DISPLAY

# Display the current weather (works just with complete data input)
def display_current_weather(data):
    #print(data)
    if data:
        print("Current Weather Information:")
        print("---------------------------")
        print(f"City: {data['name']}")
        print(f"Temperature: {data['main']['temp']}°C")
        print(f"Humidity: {data['main']['humidity']}%")
        print(f"Wind Speed: {data['wind']['speed']} m/s")
        try:
                print(f"Rain: {data['rain']['1h']} mm")
        except KeyError:
            print("No Rain")
    else:
        print("No current weather data available.")

# Display the forecast (works just with complete data input)
def display_forecast(forecast_data):
    if forecast_data:
        print("\n5-Day Forecast:")
        print("---------------")
        for forecast in forecast_data['list']:
            timestamp = datetime.fromtimestamp(forecast['dt'])
            date = timestamp.strftime('%Y-%m-%d')
            time = timestamp.strftime('%H:%M')
            print(f"Date: {date} Time: {time}")
            print(f"Temperature: {forecast['main']['temp']}°C")
            print(f"Humidity: {forecast['main']['humidity']}%")
            print(f"Wind Speed: {forecast['wind']['speed']} m/s")
            try:
                print(f"Rain: {forecast['rain']['3h']} mm/3h")
            except KeyError:
                print("No Rain")

   
            print()
    else:
        print("No forecast data available.")
'''