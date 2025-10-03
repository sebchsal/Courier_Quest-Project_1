import pygame
from abc import ABC, abstractmethod
from tools.inventory import Inventory   # Inventario para pedidos

class Player:
    def __init__(self, x, y, estrategia, tile_size=50, max_weight=5):
        self.x = x
        self.y = y
        self.vel = 5
        self.estrategia = estrategia
        self.tile_size = tile_size
        self.inventory = Inventory(max_weight)
        # Resistencia 
        self.stamina = 100
        self.recovery_threshold = 30
        self.last_move_time = 0
        # Reputación  
        self.reputation = 70
        self.streak = 0
        self.first_late_penalty_used = False
        # Escalado
        scale = int(tile_size * 1.2)
        # Sistemas de puntaje
        self.total_payments = 0 # Total de pagos recibidos
        self.penalties = 0 # Total de penalizaciones
        self.final_score = 0 # Puntaje final
        # Cargar sprites según dirección
        self.sprites = {
            "down": pygame.transform.scale(pygame.image.load("images/delivery_down.png").convert_alpha(), (scale, scale)),
            "up": pygame.transform.scale(pygame.image.load("images/delivery_up.png").convert_alpha(), (scale, scale)),
            "left": pygame.transform.scale(pygame.image.load("images/delivery_left.png").convert_alpha(), (scale, scale)),
            "right": pygame.transform.scale(pygame.image.load("images/delivery_right.png").convert_alpha(), (scale, scale))
        }
        self.sprite = self.sprites["down"]
        self.width = scale
        self.height = scale
    # Actualizar reputación
    def update_reputation (self, change, reason=""):
        old = self.reputation
        self.reputation = max(0, min(100, self.reputation + change))
        print(f"🔔 Reputación {old} -> {self.reputation} ({reason})") # Actualización de reputación, se ve en consola

        if self.reputation < 20:
            print("❌ Derrota inmediata por reputación baja") # Derrota inmediata, se ve en cosola
            return "defeat"
        return "ok"
    
    # Aplicar bonus de reputación al payout
    def apply_payout_bonus(self, payout):
        if self.reputation >= 90:
            return payout * 1.05
        return payout
    
    # Estados del repartidor
    def get_state(self):
        if self.stamina <= 0:
            return "exhausted"
        elif self.stamina <= 30:
            return "tired"
        return "normal"
    
    # Velocidad según estado
    def get_speed(self, clima, mapa=None):
        state = self.get_state()
        # Exhausto y sin llegar al 30% → no puede moverse
        if state == "exhausted" and self.stamina < 30:
            return 0
        # Velocidad base y multiplicadores
        v0 = 4  
        Mclima = clima.get_multiplier()
        peso_total = self.inventory.total_weight()
        Mpeso = max(0.8, 1 - 0.03 * peso_total)
        Mrep = 1.03 if self.reputation >= 90 else 1.0
        if state == "tired":
            Mres = 0.8
        elif state == "exhausted":
            Mres = 0.0
        else:
            Mres = 1.0
        surface = 1.0
        if mapa is not None:
            tile_x = int(self.x // self.tile_size)
            tile_y = int(self.y // self.tile_size)
            if 0 <= tile_x < mapa.width and 0 <= tile_y < mapa.height:
                surface = mapa.weight_surface(tile_x, tile_y)
        # Fórmula completa sugerida
        v = v0 * Mclima * Mpeso * Mrep * Mres * surface
        return v
    
    # Consumo de stamina
    def stamina_cost(self, clima):
        cost = 0.5  # base
        extra_weight = max(0, self.inventory.total_weight() - 3)
        cost += 0.2 * extra_weight
        if clima.current_condition in ("rain", "wind"):
            cost += 0.1
        elif clima.current_condition == "storm":
            cost += 0.3
        elif clima.current_condition == "heat":
            cost += 0.2
        return cost
    
    # Recuperación de stamina
    def recover(self, dt, resting=False):
        amount = 10 * dt if resting else 5 * dt
        self.stamina = min(100, self.stamina + amount)

    # Movimiento
    def mover(self, teclas, mapa, clima):
        old_x, old_y = self.x, self.y
        speed = self.get_speed(clima, mapa)
        self.estrategia.mover(self, teclas, speed)
        # Limites del mapa
        max_x = mapa.width * self.tile_size - self.width
        max_y = mapa.height * self.tile_size - self.height
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))
        # Colisión con parques (mantener edificios atravesables)
        tile_x = int(self.x // self.tile_size)
        tile_y = int(self.y // self.tile_size)
        # tile de parque
        if mapa.tiles[tile_y][tile_x] == "P": self.x, self.y = old_x, old_y
        # tile de descanso
        moved = (self.x != old_x or self.y != old_y)
        if moved and speed > 0:
            self.stamina -= self.stamina_cost(clima)
            self.stamina = max(0, self.stamina)
        return moved
    
    # Dibujar sprite
    def dibujar(self, surface, offset_x, offset_y):
        surface.blit(self.sprite, (self.x - offset_x, self.y - offset_y))

# Estrategias de movimiento
class MovimientoStrategy(ABC):
    @abstractmethod
    def mover(self, jugador, teclas, speed=0):
        pass
# Flechas o WASD paara moverse
class MovimientoFlechas(MovimientoStrategy):
    def mover(self, jugador, teclas, speed=0):
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            jugador.x -= speed
            jugador.sprite = jugador.sprites["left"]
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            jugador.x += speed
            jugador.sprite = jugador.sprites["right"]
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            jugador.y -= speed
            jugador.sprite = jugador.sprites["up"]
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            jugador.y += speed
            jugador.sprite = jugador.sprites["down"]
