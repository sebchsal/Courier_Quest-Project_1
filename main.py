import sys
import pygame

from map import Mapa, map_data
from jobs import Packet, jobs_data, pickup_img, dropoff_img
from weather import Weather, weather_data
from player import Player, MovimientoFlechas
from building import detectar_bloques
from road import detectar_calles
from park import detectar_parques
from tools.clean_all import clean_all   # Limpieza automática

# Ejecutar limpieza al inicio y mostrar resumen
summary = clean_all()
if summary:
    print("🧹 Limpieza completada:")
    for base, removed in summary.items():
        print(f"  {base}: borrados {len(removed)} → {', '.join(removed)}")
else:
    print("✅ No había versiones antiguas que borrar.")

# --- Inicializar pygame ---
pygame.init()
ANCHO_VENTANA, ALTO_VENTANA = 800, 600
ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("Courier Quest - Ciudad Modular")

# --- Configuración del mapa ---
TILE_SIZE = 80
mapa = Mapa(map_data)
clima = Weather(weather_data)
pedidos = [Packet.from_dict(p) for p in jobs_data]

# --- Convertir y escalar imágenes de pedidos (ya con display inicializado) ---
pickup_img = pygame.transform.scale(pickup_img.convert_alpha(), (TILE_SIZE, TILE_SIZE))
dropoff_img = pygame.transform.scale(dropoff_img.convert_alpha(), (TILE_SIZE, TILE_SIZE))

# --- Jugador ---
jugador = Player(100, 100, MovimientoFlechas(), TILE_SIZE)

# --- Detectar edificios como bloques ---
bloques_edificios = detectar_bloques(mapa, TILE_SIZE, "images/building.png")
bloques_calles = detectar_calles(mapa, TILE_SIZE, "images/road.jpg")

# --- Detectar parques como bloques ---
bloques_parques = detectar_parques(mapa, TILE_SIZE, "images/park.png")

# --- Dibujar mapa (sin edificios) ---
def dibujar_mapa(surface, mapa: Mapa, offset_x, offset_y):
    for y, fila in enumerate(mapa.tiles):
        for x, tile in enumerate(fila):
            draw_x = x * TILE_SIZE - offset_x
            draw_y = y * TILE_SIZE - offset_y
            if -TILE_SIZE < draw_x < ANCHO_VENTANA and -TILE_SIZE < draw_y < ALTO_VENTANA:
                if tile == "D":  # drop/pickup inválido
                    pygame.draw.rect(surface, (200, 0, 0), (draw_x, draw_y, TILE_SIZE, TILE_SIZE))

# --- Dibujar pedidos (centrados en el tile) ---
def dibujar_pedidos(surface, pedidos, offset_x, offset_y):
    for pedido in pedidos:
        px, py = pedido.pickup
        dx, dy = pedido.dropoff
        # Posiciones centradas
        pickup_x = px * TILE_SIZE + (TILE_SIZE - pickup_img.get_width()) // 2 - offset_x
        pickup_y = py * TILE_SIZE + (TILE_SIZE - pickup_img.get_height()) // 2 - offset_y
        dropoff_x = dx * TILE_SIZE + (TILE_SIZE - dropoff_img.get_width()) // 2 - offset_x
        dropoff_y = dy * TILE_SIZE + (TILE_SIZE - dropoff_img.get_height()) // 2 - offset_y
        # Dibujar imágenes
        surface.blit(pickup_img, (pickup_x, pickup_y))
        surface.blit(dropoff_img, (dropoff_x, dropoff_y))

# --- Cámara ---
def calcular_offset(jugador, mapa, ANCHO_VENTANA, ALTO_VENTANA, TILE_SIZE):
    offset_x = jugador.x - ANCHO_VENTANA // 2
    offset_y = jugador.y - ALTO_VENTANA // 2
    # Limitar offset para no salir del mapa
    max_offset_x = mapa.width * TILE_SIZE - ANCHO_VENTANA
    max_offset_y = mapa.height * TILE_SIZE - ALTO_VENTANA
    offset_x = max(0, min(offset_x, max_offset_x))
    offset_y = max(0, min(offset_y, max_offset_y))

    return offset_x, offset_y

# --- Bucle principal ---
clock = pygame.time.Clock()
fuente = pygame.font.SysFont("Arial", 18)
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    teclas = pygame.key.get_pressed()
    jugador.mover(teclas, mapa)

    offset_x, offset_y = calcular_offset(jugador, mapa, ANCHO_VENTANA, ALTO_VENTANA, TILE_SIZE)

    ventana.fill((255, 255, 255))

    # Calles primero
    for c in bloques_calles:
        c.dibujar(ventana, offset_x, offset_y)

    # Parques encima de calles pero debajo de edificios
    for p in bloques_parques:
        p.dibujar(ventana, offset_x, offset_y)

    # Edificios primero
    for b in bloques_edificios:
        b.dibujar(ventana, offset_x, offset_y)

    # Terreno base
    dibujar_mapa(ventana, mapa, offset_x, offset_y)

    # Jugador
    jugador.dibujar(ventana, offset_x, offset_y)

    # Pedidos encima de edificios
    dibujar_pedidos(ventana, pedidos, offset_x, offset_y)

    # HUD
    texto = f"{mapa.cityname} | Clima: {clima.initial['condition']} | Pedidos: {len(pedidos)}"
    ventana.blit(fuente.render(texto, True, (255, 255, 255)), (10, 10))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
sys.exit()