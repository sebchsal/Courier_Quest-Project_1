import json
import os
import requests
from datetime import datetime
from objects.jobs import Packet

# Helpers para obtener datos con caché y fallback local
def get_data_with_cache(url, cache_path, local_fallback=None):
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    # Intentar obtener datos de la API
    try:
        # Hacer solicitud HTTP con timeout
        res = requests.get(url, timeout=5)
        res.raise_for_status()
        data = res.json()
        # Guardar con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        versioned_path = f"{cache_path}_{timestamp}"
        # Guardar en cache y versiónada
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # Guardar versiónada
        with open(versioned_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        # Retornar datos de la API
        return data
    except Exception: # Cualquier error (conexión, JSON, etc)
        # Intentar cargar desde caché
        if os.path.exists(cache_path): # Si existe caché
            # Cargar y retornar datos de caché
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif local_fallback and os.path.exists(local_fallback):
            # Cargar y retornar datos del fallback local
            with open(local_fallback, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            raise RuntimeError(f"No hay datos en API, cache ni fallback local ({local_fallback}).")

# Cargar datos del mapa 
url = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map"
cache_path = "api_cache/map.json"
local_path = "data/city.json"
raw_map = get_data_with_cache(url, cache_path, local_path)
map_data = raw_map["data"] if "data" in raw_map else raw_map

# Clase Mapa 
class Mapa:
    def __init__(self, data: dict):
        self.width = data["width"]
        self.height = data["height"]
        self.tiles = data["tiles"]
        self.legend = data["legend"]
        self.cityname = data.get("city_name", "")
        self.goal = data.get("goal", 0)
        self.maxtime = data.get("max_time", 0)
    # Verificar si es calle o paquete (atravesable)
    def street_verification(self, x: int, y: int) -> bool:
        tile = self.tiles[y][x]
        return tile in ("C", "D")
    # Verificar si hay un punto de entrega
    def weight_surface(self, x: int, y: int) -> float:
        tile = self.tiles[y][x]
        return self.legend[tile].get("surface_weight", 1.0)
    # Marcar punto de entrega
    def package_insercion(self, paquete: Packet):
        x, y = paquete.pickup
        if not self.street_verification(x, y):
            self.tiles[y][x] = "D"
    # Marcar punto de descanso
    def is_rest_point(self, x: int, y: int) -> bool:
        return self.tiles[y][x] == "R"
