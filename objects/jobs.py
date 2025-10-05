import json
import random
import time
import os
import pygame
import requests
from datetime import datetime

# Lista de pedidos base para reposición
base_packets = []

# Cargar las imágenes de pedidos (sin convert_alpha aún) 
pickup_img = pygame.image.load("images/pckup.png")
dropoff_img = pygame.image.load("images/drop.png")

# Helpers para obtener datos con caché y fallback local
def get_data_with_cache(url, cache_path, local_fallback=None):
    os.makedirs(os.path.dirname(cache_path), exist_ok=True) # Asegurar que el directorio existe
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
        elif local_fallback and os.path.exists(local_fallback): # Si existe fallback local
            # Cargar y retornar datos del fallback local
            with open(local_fallback, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            raise RuntimeError(f"No hay datos en API, cache ni fallback local ({local_fallback}).")

# Cargar datos de jobs 
url = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/jobs"
cache_path = "api_cache/jobs.json"
local_path = "data/pedidos.json"
raw_jobs = get_data_with_cache(url, cache_path, local_path) # Puede ser lista o dict con "data"
jobs_data = raw_jobs["data"] if "data" in raw_jobs else raw_jobs # Extraer lista si es dict

# Clase Packet
class Packet:
    def __init__(self, id, pickup, dropoff, payout, deadline, weight, priority, release_time):
        self.id = id
        self.pickup = tuple(pickup)
        self.dropoff = tuple(dropoff)
        self.payout = payout
        self.deadline = deadline
        self.weight = weight
        self.priority = priority  # 0 = normal, >0 = más prioritario
        self.release_time = release_time
        self.accepted_time = None  # Tiempo cuando se aceptó el pedido
    # Método de clase para crear un Packet a partir de un diccionario
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
    # Representación para depuración
    def __repr__(self):
        return f"<Packet {self.id} P:{self.priority} W:{self.weight} D:{self.deadline}>"

# Estado de pedidos
pickups_disponibles = []
activos = []
completados = []
todos_los_pedidos = []

# Inicializar pedidos 
def inicializar_pedidos(jobs_data): # jobs_data es una lista de dicts
    global todos_los_pedidos, pickups_disponibles, activos, completados, base_packets

    base_packets = [Packet.from_dict(p) for p in jobs_data]  # copia plantilla
    todos_los_pedidos = [Packet.from_dict(p) for p in jobs_data]
    pickups_disponibles = todos_los_pedidos[:]
    activos = []
    completados = []
    return pickups_disponibles # Retornar lista inicial

# Dibujar pedidos 
def dibujar_pedidos(surface, offset_x, offset_y, TILE_SIZE, pickup_surf, dropoff_surf):
    # Pickups disponibles
    for pedido in pickups_disponibles: # Pedidos con pickup en el mapa
        px, py = pedido.pickup
        x = px * TILE_SIZE + (TILE_SIZE - pickup_surf.get_width()) // 2 - offset_x
        y = py * TILE_SIZE + (TILE_SIZE - pickup_surf.get_height()) // 2 - offset_y
        surface.blit(pickup_surf, (x, y))

    # Dropoffs de pedidos activos
    for pedido in activos: # Pedidos en inventario con dropoff en el mapa
        dx, dy = pedido.dropoff
        x = dx * TILE_SIZE + (TILE_SIZE - dropoff_surf.get_width()) // 2 - offset_x
        y = dy * TILE_SIZE + (TILE_SIZE - dropoff_surf.get_height()) // 2 - offset_y
        surface.blit(dropoff_surf, (x, y))

# Aceptar pedido 
def aceptar_pedido(tile_x, tile_y, jugador):
    global pickups_disponibles, activos # todos los pedidos
    candidato = None
    for p in pickups_disponibles: # Buscar pedido con pickup en la posición
        if (p.pickup[0], p.pickup[1]) == (tile_x, tile_y):
            candidato = p
            break
    if candidato: # Si se encontró un pedido para aceptar
        if jugador.inventory.add(candidato):
            pickups_disponibles.remove(candidato)
            candidato.accepted_time = time.time()
            activos.append(candidato)
            return True
    return False

# Helpers para reposición 
def es_calle(mapa, x, y):
    return mapa.tiles[y][x] == "C"

def es_edificio(mapa, x, y):
    return mapa.tiles[y][x] == "B"

# Vecinos 4-direccionales 
def vecinos_4(mapa, x, y):
    for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)): # Derecha, Izquierda, Abajo, Arriba
        nx, ny = x+dx, y+dy # Nueva posición
        if 0 <= nx < mapa.width and 0 <= ny < mapa.height: # Dentro de límites
            yield nx, ny # Retornar vecino válido

# Posiciones de calles adyacentes a edificios 
def posiciones_calle_adyacente_a_building(mapa): 
    posiciones = set() # Usar set para evitar duplicados
    for y in range(mapa.height): # Iterar filas
        for x in range(mapa.width): # Iterar columnas
            # Verificar si es un edificio
            if es_edificio(mapa, x, y):
                for nx, ny in vecinos_4(mapa, x, y): # Vecinos 4-direccionales
                    if es_calle(mapa, nx, ny):
                        posiciones.add((nx, ny))
    return list(posiciones) # Convertir a lista

# Crear nuevo pickup 
def crear_nuevo_pickup(base_packet, mapa): 
    candidatos = posiciones_calle_adyacente_a_building(mapa) # Pickups cerca de edificios
    if not candidatos: # Fallback si no hay edificios
        candidatos = [(x, y) for y in range(mapa.height) for x in range(mapa.width) if es_calle(mapa, x, y)]
    px, py = random.choice(candidatos)
    # Elegir dropoff en cualquier calle
    calles = [(x, y) for y in range(mapa.height) for x in range(mapa.width) if es_calle(mapa, x, y)]
    dx, dy = random.choice(calles)
    return Packet(
        id=f"{base_packet.id}-R{int(time.time())}",
        pickup=(px, py),
        dropoff=(dx, dy),
        payout=base_packet.payout,
        deadline=base_packet.deadline,
        weight=base_packet.weight,
        priority=base_packet.priority,
        release_time=base_packet.release_time 
    )

# Reponer tanda de pedidos base de la API
def reponer_tanda_base():
    global pickups_disponibles, base_packets
    if not base_packets:
        return []
    # Elimina cualquier pickup pendiente de la tanda anterior
    pickups_disponibles.clear()
    # Recrear los mismos 5 paquetes base con las mismas posiciones
    nuevos = []
    for bp in base_packets:
        # Clonar sin alterar pickup/dropoff
        nuevo = Packet(
            id=bp.id,
            pickup=bp.pickup,
            dropoff=bp.dropoff,
            payout=bp.payout,
            deadline=bp.deadline,
            weight=bp.weight,
            priority=bp.priority,
            release_time=bp.release_time
        )
        nuevos.append(nuevo)
    pickups_disponibles.extend(nuevos)
    return nuevos

# Verificar entrega 
def verificar_entrega(tile_x, tile_y, jugador, mapa):
    global activos, completados, pickups_disponibles
    entregado = None
    for p in activos:
        if (p.dropoff[0], p.dropoff[1]) == (tile_x, tile_y):
            entregado = p
            break

    if not entregado:
        return False

    # Verificar tiempo de entrega
    if entregado.accepted_time:
        elapsed = time.time() - entregado.accepted_time
        limit = 30
        remaining = limit - elapsed

        # reputación según tiempo
        if remaining >= limit * 0.2:
            jugador.update_reputation(+5, "Entrega temprana")
        elif remaining >= 0:
            jugador.update_reputation(+3, "Entrega a tiempo")
        else:
            late = abs(remaining)
            if late <= 30:
                penalty = -2
            elif late <= 120:
                penalty = -5
            else:
                penalty = -10
            if jugador.reputation >= 85 and not jugador.first_late_penalty_used:
                penalty //= 2
                jugador.first_late_penalty_used = True
            jugador.update_reputation(penalty, "Entrega tardía")

        # Racha de entregas
        if jugador.reputation >= 20:
            jugador.streak += 1
            if jugador.streak == 3:
                jugador.update_reputation(+2, "Racha 3 entregas")
                jugador.streak = 0
        else:
            jugador.streak = 0

        # Pago
        pago_final = jugador.apply_payout_bonus(entregado.payout)
        jugador.total_payments += pago_final

        # Mover pedido de activos a completados
        activos.remove(entregado)
        completados.append(entregado)
        jugador.inventory.remove_by_id(entregado.id)
        verificar_mapa_vacio_y_reponer()
        try:
            if base_packets and len(completados) >= len(base_packets):
                # Reponer los mismos 5 pedidos base de la API
                reponer_tanda_base()
                completados.clear()
        except Exception as e:
            print("Error al reponer tanda base:", e)

        return True
    return False

# Verificar mapa vacío y reponer pedidos
def  verificar_mapa_vacio_y_reponer():
    global pickups_disponibles, activos, base_packets, completados

    # Si ya no hay pickups ni dropoffs (ni activos ni disponibles)
    if not pickups_disponibles and not activos:
        print("Mapa vacío detectado → regenerando los 5 paquetes base...")
        reponer_tanda_base()
        completados.clear()

# Cancelar pedido
def cancelar_pedido(pedido, jugador):
    global activos
    if pedido in activos:
        activos.remove(pedido)   # ya no se dibuja dropoff
        jugador.update_reputation(-4, f"Cancelar pedido {pedido.id}")
        jugador.penalties += 4
        verificar_mapa_vacio_y_reponer()

# Expirar pedido
def expirar_pedido(pedido, jugador):
    global activos, pickups_disponibles # todos_los_pedidos
    now = time.time() # Tiempo actual

    # Verifica si el pedido está activo y ha pasado 30 segundos desde que fue aceptado
    if pedido in activos:
        # Verifica si el pedido tiene tiempo de aceptación y ha pasado el límite
        if pedido.accepted_time and now > pedido.accepted_time + 30:
            activos.remove(pedido)
            jugador.inventory.remove_by_id(pedido.id)
            jugador.update_reputation(-6, "Pedido expirado")
            jugador.penalties += 6
            print(f"Pedido {pedido.id} expirado...")
    elif pedido in pickups_disponibles: # Si el pedido nunca fue aceptado y ha pasado su release_time
        pickups_disponibles.remove(pedido)
        jugador.update_reputation(-6, "Pedido perdido antes de aceptar")
        jugador.penalties += 6
        print(f"Pedido {pedido.id} perdido antes de ser aceptado...")
    verificar_mapa_vacio_y_reponer()