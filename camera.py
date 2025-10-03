
class Camera:
    def __init__(self, ancho_ventana, alto_ventana, tile_size):
        self.ancho = ancho_ventana
        self.alto = alto_ventana
        self.tile_size = tile_size

    def calcular_offset(self, jugador, mapa):
        offset_x = jugador.x - self.ancho // 2
        offset_y = jugador.y - self.alto // 2
        max_offset_x = mapa.width * self.tile_size - self.ancho
        max_offset_y = mapa.height * self.tile_size - self.alto
        offset_x = max(0, min(offset_x, max_offset_x))
        offset_y = max(0, min(offset_y, max_offset_y))
        return offset_x, offset_y