import json
import os
import requests
import random
import time
from datetime import datetime

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
        if os.path.exists(cache_path):
            # Cargar y retornar datos de caché
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        elif local_fallback and os.path.exists(local_fallback):
            # Cargar y retornar datos del fallback local
            with open(local_fallback, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            raise RuntimeError(f"No hay datos en API, cache ni fallback local ({local_fallback}).")

# Cargar datos de clima
url = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/weather"
cache_path = "api_cache/weather.json"
local_path = "data/weather.json"
raw_weather = get_data_with_cache(url, cache_path, local_path)

weather_data = raw_weather["data"] if "data" in raw_weather else raw_weather

# Multiplicadores de velocidad base
SPEED_MULTIPLIERS = {
    "clear": 1.00,
    "clouds": 0.98,
    "rain_light": 0.90,
    "rain": 0.85,
    "storm": 0.75,
    "fog": 0.88,
    "wind": 0.92,
    "heat": 0.90,
    "cold": 0.92
}

# Interpolación lineal entre dos valores. Ej: lerp(0, 100, 0.5) = 50
def lerp(a, b, t):
    return a + (b - a) * t

# Clase weather, gestiona el clima dinámico con transiciones y efectos en la velocidad del juego/simulación
class Weather:
    def __init__(self, data: dict):
        # Datos básicos de configuración
        self.city = data["city"]
        self.initial = data["initial"]
        self.conditions = data["conditions"]
        self.transitions = data["transition"]

        # Estado actual del clima
        self.current_condition = self.initial["condition"]
        self.intensity = random.uniform(0.3, 1.0)

        # Multiplicadores de velocidad
        self.current_multiplier = SPEED_MULTIPLIERS[self.current_condition]
        self.start_multiplier = self.current_multiplier
        self.target_multiplier = self.current_multiplier

        # Bursts dinámicos (45–60s)
        self.burst_start = time.time()
        self.burst_duration = random.randint(45, 60)

        # Sistema de las transiciones 
        self.transition_start = None
        self.transition_duration = 0
        self.target_condition = self.current_condition

    # Actualiza el estado del clima, se llama en cada frame/tick del juego
    def update(self):
        now = time.time()

        elapsed = now - self.burst_start
        if elapsed >= self.burst_duration and not self.transition_start:
            self.target_condition = self.next_condition()
            self.start_multiplier = self.current_multiplier
            self.target_multiplier = SPEED_MULTIPLIERS[self.target_condition]
            self.transition_start = now
            self.transition_duration = random.uniform(3, 5)
            self.intensity = random.uniform(0.3, 1.0)
            self.burst_start = now
            # Nuevo burst aleatorio entre 45–60s
            self.burst_duration = random.randint(45, 60)

        if self.transition_start:
            t = (now - self.transition_start) / self.transition_duration
            if t >= 1.0:
                self.current_condition = self.target_condition
                self.current_multiplier = self.target_multiplier
                self.transition_start = None
            else:
                self.current_multiplier = lerp(self.start_multiplier, self.target_multiplier, t)

    # Determinar la próxima condición climática basándose en probabilidades de transición
    def next_condition(self):
        probs = self.transitions.get(self.current_condition, {})
        if not probs:
            return random.choice(self.conditions)

        total = sum(probs.values())
        r = random.random()
        acc = 0.0
        for cond, p in probs.items():
            acc += p / total
            if r <= acc:
                return cond
        return self.current_condition

    # Se obtiene el multiplicador de velocidad actual
    def get_multiplier(self):
        return self.current_multiplier

    # Se obtiene un diccionario con el estado completo del clima
    def get_status(self):
        return {
            "condition": self.current_condition, # Condición climática actual
            "multiplier": round(self.current_multiplier, 3), # Multiplicador redondeado a 3 decimales
            "intensity": round(self.intensity, 2), # Intensidad redondeada a 2 decimales
            "next": self.target_condition if self.transition_start else None # Siguiente condición o None
        }