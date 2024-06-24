import csv
import json

def convert_csv_to_json(csv_file_path, json_file_path):
    region_dict = {}

    # Legge il file CSV con codifica 'latin1'
    with open(csv_file_path, mode='r', encoding='latin1') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=';')
        
        for row in csvreader:
            regione = row['denominazione_regione']
            provincia = row['denominazione_provincia']
            comune = row['denominazione_ita']
            latitudine = row['lat']
            longitudine = row['lon']
            cap = row['cap']
            
            if regione not in region_dict:
                region_dict[regione] = {}
            
            if provincia not in region_dict[regione]:
                region_dict[regione][provincia] = set()
            
            # Aggiunge le informazioni della città come un dizionario
            city_info = {
                'nome': comune,
                'latitudine': latitudine,
                'longitudine': longitudine,
                'cap': cap
            }
            
            # Aggiunge il dizionario della città al set per evitare duplicati
            region_dict[regione][provincia].add(json.dumps(city_info))

    # Ordina regioni, province e comuni
    sorted_region_dict = {
        regione: {
            provincia: sorted(
                [json.loads(city) for city in cities],
                key=lambda x: x['nome']
            )
            for provincia, cities in sorted(province_dict.items())
        }
        for regione, province_dict in sorted(region_dict.items())
    }

    # Scrive il file JSON
    with open(json_file_path, mode='w', encoding='utf-8') as jsonfile:
        json.dump(sorted_region_dict, jsonfile, ensure_ascii=False, indent=4)

# Funzione per caricare il JSON in un dizionario
def load_json_to_dict(json_file_path):
    with open(json_file_path, mode='r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)
    return data

# Utilizzo
csv_file_path = 'COMUNI.csv'  # Percorso del tuo file CSV
json_file_path = 'COMUNI.json'  # Percorso del file JSON che vuoi creare
convert_csv_to_json(csv_file_path, json_file_path)

# Carica i dati JSON in una variabile Python
italy_data = load_json_to_dict(json_file_path)

