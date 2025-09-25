import json
import os
import requests
from datetime import datetime
import pygame

# --- Cargar imágenes de pedidos (sin convert_alpha aún) ---
pickup_img = pygame.image.load("images/pckup.png")
dropoff_img = pygame.image.load("images/drop.png")

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

# --- Cargar datos de jobs ---
url = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/jobs"
cache_path = "api_cache/jobs.json"
local_path = "data/pedidos.json"
raw_jobs = get_data_with_cache(url, cache_path, local_path)

jobs_data = raw_jobs["data"] if "data" in raw_jobs else raw_jobs

# --- Clase Packet ---
class Packet:
    def __init__(self, id, pickup, dropoff, payout, deadline, weight, priority, release_time):
        self.id = id
        self.pickup = tuple(pickup)
        self.dropoff = tuple(dropoff)
        self.payout = payout
        self.deadline = deadline
        self.weight = weight
        self.priority = priority
        self.release_time = release_time

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            id=data["id"],
            pickup=data["pickup"],
            dropoff=data["dropoff"],
            payout=data["payout"],
            deadline=data["deadline"],
            weight=data["weight"],
            priority=data["priority"],
            release_time=data["release_time"]
        )