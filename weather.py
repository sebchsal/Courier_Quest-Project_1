import json
import os
import requests
from datetime import datetime

def get_data_with_cache(url, cache_path, local_fallback=None):
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    try:
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()

        # Guardar con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        versioned_path = f"{cache_path}_{timestamp}"
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        with open(versioned_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        return data
    except Exception:
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif local_fallback and os.path.exists(local_fallback):
            with open(local_fallback, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            raise RuntimeError(f"No hay datos en API, cache ni fallback local ({local_fallback}).")

# --- Cargar datos de clima ---
url = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/weather"
cache_path = "api_cache/weather.json"
local_path = "data/weather.json"
raw_weather = get_data_with_cache(url, cache_path, local_path)

weather_data = raw_weather["data"] if "data" in raw_weather else raw_weather

# --- Clase Weather ---
class Weather:
    def __init__(self, data: dict):
        self.city = data["city"]
        self.initial = data["initial"]
        self.conditions = data["conditions"]
        self.transitions = data["transition"]
