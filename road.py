import pygame

class Road:
    def __init__(self, x, y, tile_size=40, img_path="images/road.jpg"):
        self.x = x
        self.y = y
        self.tile_size = tile_size

        try:
            raw_img = pygame.image.load(img_path).convert_alpha()
        except pygame.error:
            print(f"Error cargando imagen: {img_path}")
            raw_img = pygame.Surface((tile_size, tile_size))
            raw_img.fill((37, 37, 37))

        # Escalar al tamaño de un tile
        self.sprite = pygame.transform.scale(raw_img, (tile_size, tile_size))

    def dibujar(self, surface, offset_x, offset_y):
        draw_x = self.x * self.tile_size - offset_x
        draw_y = self.y * self.tile_size - offset_y

        # Solo dibujar si está en pantalla
        if (draw_x < -self.tile_size or draw_x > surface.get_width() or
            draw_y < -self.tile_size or draw_y > surface.get_height()):
            return

        surface.blit(self.sprite, (draw_x, draw_y))


def detectar_calles(mapa, tile_size=40, img_path="images/road.jpg"):
    calles = []
    for y in range(mapa.height):
        for x in range(mapa.width):
            if mapa.tiles[y][x] == "C":
                calles.append(Road(x, y, tile_size, img_path))
    return calles
