import os
import json
import time
import pickle

DATA_DIR = "data"
SCORES_PATH = os.path.join(DATA_DIR, "puntajes.json")
SAVEGAME_BIN = os.path.join(DATA_DIR, "savegame.bin")

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

# Score en .json
def load_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def save_json(path, obj):
    ensure_data_dir()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def append_score_record(nombre, score, extra=None, max_items=50):
    """Guarda el puntaje en la cola y JSON, ordenado de mayor a menor"""
    ensure_data_dir()
    data = load_json(SCORES_PATH, [])
    record = {
        "nombre": nombre,
        "score": int(score),
        "timestamp": int(time.time()),
    }
    if extra:
        record.update(extra)
    data.append(record)
    data = sorted(data, key=lambda r: r["score"], reverse=True)
    if len(data) > max_items:
        data = data[:max_items]
    save_json(SCORES_PATH, data)
    return data

# Partidoa binaria
def save_game_binary(state):
    """Guarda el estado del juego en formato binario."""
    ensure_data_dir()
    with open(SAVEGAME_BIN, "wb") as f:
        pickle.dump(state, f)

def load_game_binary():
    """Carga una partida binaria."""
    try:
        with open(SAVEGAME_BIN, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None