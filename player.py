import pygame
from abc import ABC, abstractmethod


class Player:
    def __init__(self, x, y, estrategia, tile_size=50):
        self.x = x
        self.y = y
        self.vel = 5
        self.estrategia = estrategia
        self.tile_size = tile_size
        # Escalado
        scale = int(tile_size * 0.8)
        # Cargar sprites según dirección
        self.sprites = {
            "down": pygame.transform.scale(pygame.image.load("images/delivery_down.png").convert_alpha(), (scale, scale)),
            "up": pygame.transform.scale(pygame.image.load("images/delivery_up.png").convert_alpha(), (scale, scale)),
            "left": pygame.transform.scale(pygame.image.load("images/delivery_left.png").convert_alpha(), (scale, scale)),
            "right": pygame.transform.scale(pygame.image.load("images/delivery_right.png").convert_alpha(), (scale, scale))
        }
        # Sprite inicial mirando hacia abajo
        self.sprite = self.sprites["down"]
        # Ajustar colisiones al nuevo tamaño
        self.width = scale
        self.height = scale

    def mover(self, teclas, mapa):
        old_x, old_y = self.x, self.y
        self.estrategia.mover(self, teclas)
        # Limites del mapa
        max_x = mapa.width * self.tile_size - self.width
        max_y = mapa.height * self.tile_size - self.height
        self.x = max(0, min(self.x, max_x))
        self.y = max(0, min(self.y, max_y))
        # Colisión con edificios
        tile_x = self.x // self.tile_size
        tile_y = self.y // self.tile_size
        if not mapa.street_verification(tile_x, tile_y):
            self.x, self.y = old_x, old_y

    def dibujar(self, surface, offset_x, offset_y):
        surface.blit(self.sprite, (self.x - offset_x, self.y - offset_y))

class MovimientoStrategy(ABC):
    @abstractmethod
    def mover(self, jugador, teclas):
        pass

class MovimientoFlechas(MovimientoStrategy):
    def mover(self, jugador, teclas):
        if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
            jugador.x -= jugador.vel
            jugador.sprite = jugador.sprites["left"]
        if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
            jugador.x += jugador.vel
            jugador.sprite = jugador.sprites["right"]
        if teclas[pygame.K_UP] or teclas[pygame.K_w]:
            jugador.y -= jugador.vel
            jugador.sprite = jugador.sprites["up"]
        if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
            jugador.y += jugador.vel
            jugador.sprite = jugador.sprites["down"]
