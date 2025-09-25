import pygame

class Park:
    def __init__(self, x, y, w, h, tile_size=40, img_path="images/park.png"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.tile_size = tile_size

        raw_img = pygame.image.load(img_path).convert_alpha()
        self.sprite = pygame.transform.scale(
            raw_img, (w * tile_size, h * tile_size)
        )

    def dibujar(self, surface, offset_x, offset_y):
        draw_x = self.x * self.tile_size - offset_x
        draw_y = self.y * self.tile_size - offset_y
        # Solo dibujar si está visible en pantalla
        if (draw_x < -self.w * self.tile_size or 
            draw_x > surface.get_width() or
            draw_y < -self.h * self.tile_size or 
            draw_y > surface.get_height()):
            return
        # Dibujar rectángulo base oscuro (para debug, puedes comentarlo)
        pygame.draw.rect(surface, (109, 109, 109),
                         (draw_x, draw_y,
                          self.w * self.tile_size,
                          self.h * self.tile_size))
        # Dibujar el sprite redimensionado encima
        surface.blit(self.sprite, (draw_x, draw_y))


def detectar_parques(mapa, tile_size=40, img_path="images/park.png"):
    visitados = [[False]*mapa.width for _ in range(mapa.height)]
    parques = []

    for y in range(mapa.height):
        for x in range(mapa.width):
            if mapa.tiles[y][x] == "P" and not visitados[y][x]:
                # encontrar tamaño del bloque
                w = h = 1

                # expandir en x
                while x+w < mapa.width and mapa.tiles[y][x+w] == "P" and not visitados[y][x+w]:
                    w += 1
                # expandir en y
                while y+h < mapa.height and all(mapa.tiles[y+h][x+i] == "P" for i in range(w)):
                    h += 1

                # marcar como visitado
                for j in range(h):
                    for i in range(w):
                        visitados[y+j][x+i] = True

                parques.append(Park(x, y, w, h, tile_size, img_path))
    return parques
