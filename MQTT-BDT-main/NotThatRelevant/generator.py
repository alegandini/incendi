import json
import random
from fwi_calculator import total_fwi

# Percorso del file di destinazione
destination_file = 'synthetic_weather_data.json'

# Carica i dati delle città dal file JSON
with open('COMUNI.json', 'r', encoding='utf-8') as file:
    comuni_data = json.load(file)

# Funzione per generare valori casuali in modo che abbiano la distribuzione desiderata
def generate_weather_data(fwi_level):
    if fwi_level == 'extreme':
        temp = random.uniform(40, 50)
        hum = random.uniform(10, 20)
        wind = random.uniform(5, 15)
        rain = 0
    elif fwi_level == 'very_high':
        temp = random.uniform(25, 35)
        hum = random.uniform(20, 40)
        wind = random.uniform(3, 10)
        rain = random.uniform(0, 1)
    elif fwi_level == 'high':
        temp = random.uniform(20, 30)
        hum = random.uniform(30, 50)
        wind = random.uniform(2, 8)
        rain = random.uniform(0, 2)
    elif fwi_level == 'moderate':
        temp = random.uniform(18, 28)
        hum = random.uniform(35, 55)
        wind = random.uniform(1, 7)
        rain = random.uniform(0.5, 3)
    else:  # low
        temp = random.uniform(15, 25)
        hum = random.uniform(40, 60)
        wind = random.uniform(0, 5)
        rain = random.uniform(1, 5)
    
    fwi_value, fwi_level = total_fwi(temp, hum, rain, wind)
    
    return {
        "main": {
            "temp": temp,
            "feels_like": temp,  # Example: feels_like could be similar to temp
            "temp_min": temp - random.uniform(0, 2),
            "temp_max": temp + random.uniform(0, 2),
            "pressure": random.randint(1000, 1020),
            "humidity": hum,
            "sea_level": random.randint(1000, 1020),
            "grnd_level": random.randint(900, 1000)
        },
        "visibility": random.randint(5000, 10000),
        "wind": {
            "speed": wind,
            "deg": random.randint(0, 360),
            "gust": random.uniform(0, wind + 2)
        },
        "rain": {
            "1h": rain
        },
        "clouds": {
            "all": random.randint(0, 100)
        },
        "weather": [
            {
                "id": random.randint(500, 800),
                "main": random.choice(["Clear", "Clouds", "Rain", "Drizzle", "Thunderstorm", "Snow", "Mist"]),
                "description": random.choice(["clear sky", "few clouds", "scattered clouds", "broken clouds", "shower rain", "rain", "thunderstorm", "snow", "mist"]),
                "icon": "10d"
            }
        ],
        "coord": {
            "lon": random.uniform(6, 18),
            "lat": random.uniform(36, 47)
        },
        "dt": random.randint(1609459200, 1672444800),  # Timestamp casuale tra 2021 e 2023
        "sys": {
            "type": 2,
            "id": random.randint(1000, 9999),
            "country": "IT",
            "sunrise": random.randint(1609459200, 1609545600),
            "sunset": random.randint(1609502400, 1609588800)
        },
        "timezone": 7200,
        "id": random.randint(10000, 99999),
        "name": "City Name",  # Placeholder, replaced below
        "cod": 200
    }

# Funzione per generare dati sintetici per tutte le città
def generate_synthetic_data():
    levels = ['extreme', 'very_high', 'high', 'moderate', 'low']
    level_targets = {
        'extreme': 4,
        'very_high': 8,
        'high': 15,
        'moderate': 20,
        'low': 53
    }
    generated_cities = set()
    synthetic_data = []

    level_counts = {level: 0 for level in levels}
    
    # Genera dati per ciascun comune
    for region, provinces in comuni_data.items():
        for province, cities in provinces.items():
            for city in cities:
                city_name = city["nome"]
                if city_name in generated_cities:
                    continue

                # Rimuovi i livelli di FWI che hanno raggiunto il target dai pesi
                available_levels = [level for level in levels if level_counts[level] < level_targets[level]]
                if not available_levels:
                    # Se non ci sono più livelli disponibili, scegli un livello casuale senza pesi
                    fwi_level = random.choice(levels)
                else:
                    available_weights = [level_targets[level] - level_counts[level] for level in available_levels]
                    fwi_level = random.choices(available_levels, weights=available_weights, k=1)[0]

                city_weather_data = generate_weather_data(fwi_level)
                city_weather_data["coord"] = {
                    "lon": float(city["longitudine"].replace(',', '.')),
                    "lat": float(city["latitudine"].replace(',', '.'))
                }
                city_weather_data["name"] = city_name
                synthetic_data.append(city_weather_data)
                generated_cities.add(city_name)
                if available_levels:  # Incrementa solo se stiamo ancora bilanciando
                    level_counts[fwi_level] += 1
    
    return synthetic_data

# Genera i dati sintetici
synthetic_data = generate_synthetic_data()

# Sovrascrivi il file di destinazione se esiste già
with open(destination_file, 'w', encoding='utf-8') as outfile:
    json.dump(synthetic_data, outfile, ensure_ascii=False, indent=4)

# Stampa il numero di comuni per cui sono stati generati dati
print(f"Dati generati per {len(synthetic_data)} comuni.")
