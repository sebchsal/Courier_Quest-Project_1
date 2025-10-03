import pygame

class Building:
    def __init__(self, x, y, w, h, tile_size=40, img_path="images/building.png"):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.tile_size = tile_size
        # Cargar imagen
        try:
            raw_img = pygame.image.load(img_path).convert_alpha()
        except pygame.error:
            print(f"Error cargando imagen: {img_path}")
            raw_img = self._create_fallback_image()
        # NUEVO: Recortar automáticamente la imagen para quitar márgenes transparentes
        cropped_img = self._crop_transparent_margins(raw_img)
        # Calcular dimensiones exactas del edificio
        target_width = w * tile_size
        target_height = h * tile_size
        # Redimensionar la imagen recortada
        if hasattr(pygame.transform, 'smoothscale'):
            self.sprite = pygame.transform.smoothscale(cropped_img, (target_width, target_height))
        else:
            self.sprite = pygame.transform.scale(cropped_img, (target_width, target_height))

    def _crop_transparent_margins(self, surface):
        """Recorta los márgenes transparentes de una imagen"""
        # Obtener el rectángulo que contiene todos los píxeles no transparentes
        try:
            # Crear una máscara de los píxeles no transparentes
            mask = pygame.mask.from_surface(surface)
            bounds = mask.get_bounding_rects()
            
            if bounds:
                # Tomar el primer rectángulo (el más grande)
                crop_rect = bounds[0]
                # Si hay múltiples rectángulos, expandir para incluir todos
                for rect in bounds[1:]:
                    crop_rect = crop_rect.union(rect)
                # Recortar la imagen
                cropped = pygame.Surface(crop_rect.size, pygame.SRCALPHA)
                cropped.blit(surface, (0, 0), crop_rect)
                return cropped
            else:
                # Si no hay píxeles visibles, devolver la imagen original
                return surface
        except:
            # Si hay algún error, devolver la imagen original
            return surface

    def _create_fallback_image(self):
        """Crea una imagen de respaldo si no se puede cargar la original"""
        fallback = pygame.Surface((100, 100), pygame.SRCALPHA)
        pygame.draw.rect(fallback, (80, 80, 80, 255), (0, 0, 100, 100))
        pygame.draw.rect(fallback, (60, 60, 60, 255), (5, 5, 90, 90), 3)
        return fallback

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


def detectar_bloques(mapa, tile_size=40, img_path="images/building.png"):
    visited = [[False] * mapa.width for _ in range(mapa.height)] # matriz de visitados
    bloques = [] # lista de bloques detectados

    for y in range(mapa.height): # recorrer filas
        for x in range(mapa.width): # recorrer columnas
            if mapa.tiles[y][x] == "B" and not visited[y][x]: # Encontrar un nuevo bloque
                # Expandir hacia la derecha y abajo para encontrar el tamaño del bloque
                w = 1
                while (x + w < mapa.width and mapa.tiles[y][x + w] == "B" and 
                       not visited[y][x + w]):# expandir ancho
                    w += 1
                h = 1
                expand = True
                while expand and y + h < mapa.height: # expandir alto
                    for i in range(w): # verificar fila completa
                        if (mapa.tiles[y + h][x + i] != "B" or 
                            visited[y + h][x + i]): # no es "B" o ya visitado
                            expand = False
                            break
                    if expand: # si toda la fila es "B", expandir
                        h += 1
                # Marcar como visitados
                for yy in range(y, y + h): # marcar filas
                    for xx in range(x, x + w): # marcar columnas
                        visited[yy][xx] = True
                bloques.append(Building(x, y, w, h, tile_size, img_path)) # agregar bloque

    return bloques