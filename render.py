import pygame

class Renderer:
    def __init__(self, fuente, fuente_grande, imagenes, ventana, ancho, alto, tile_size):
        self.fuente = fuente
        self.fuente_grande = fuente_grande
        self.img = imagenes
        self.ventana = ventana
        self.ancho = ancho
        self.alto = alto
        self.tile_size = tile_size

    def dibujar_mapa(self, mapa, offset_x, offset_y):
        for y, fila in enumerate(mapa.tiles):
            for x, tile in enumerate(fila):
                draw_x = x * self.tile_size - offset_x
                draw_y = y * self.tile_size - offset_y
                if -self.tile_size < draw_x < self.ancho and -self.tile_size < draw_y < self.alto:
                    if tile == "D":
                        pygame.draw.rect(
                            self.ventana,
                            (200, 0, 0),
                            (draw_x, draw_y, self.tile_size, self.tile_size)
                        )

    def dibujar_menu_inventario(self, jugador, modo, selected_packets):
        logo_img = self.img["logo"]
        btn_delete_img = self.img["btn_delete"]
        btn_clear_img = self.img["btn_clear"]
        btn_sortp_img = self.img["btn_sortp"]
        btn_sortd_img = self.img["btn_sortd"]
        pkg_img = self.img["pkg"]

        menu_w, menu_h = 750, 500
        menu_x = self.ancho // 2 - menu_w // 2
        menu_y = self.alto // 2 - menu_h // 2
        menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)

        pygame.draw.rect(self.ventana, (40, 40, 40), menu_rect)
        pygame.draw.rect(self.ventana, (200, 200, 200), menu_rect, 3)

        # Logo de inventory
        self.ventana.blit(logo_img, (menu_x + menu_w//2 - logo_img.get_width()//2, menu_y - 40))

        pedidos = jugador.inventory.view_by_priority() if modo == "priority" else jugador.inventory.view_by_deadline()

        # Texto ESC
        txt_esc = self.fuente.render("ESC para salir", True, (180, 180, 180))
        self.ventana.blit(txt_esc, (menu_x + 10, menu_y + 10))

        x = menu_x + 50
        y = menu_y + 90
        icon_size = 50
        icon_rects = []

        for pedido in pedidos:
            rect = pygame.Rect(x, y, icon_size, icon_size)

            # borde amarillo si está seleccionado
            if pedido in selected_packets:
                pygame.draw.rect(self.ventana, (255, 255, 0), rect.inflate(10, 10), 3)

            self.ventana.blit(pkg_img, rect.topleft)
            txt_small = pygame.font.SysFont("Arial", 14).render(str(pedido.id), True, (255, 255, 0))
            self.ventana.blit(txt_small, (x, y + icon_size + 8))

            # botón eliminar
            del_rect = btn_delete_img.get_rect()
            del_rect.midtop = (x + pkg_img.get_width()//2, y + pkg_img.get_height() + 25)
            self.ventana.blit(btn_delete_img, del_rect.topleft)

            icon_rects.append((pedido, rect, del_rect))
            x += 120

        # botones inferiores
        spacing = 40
        total_width = btn_sortp_img.get_width() + btn_sortd_img.get_width() + btn_clear_img.get_width() + 2*spacing
        start_x = menu_x + menu_w//2 - total_width//2
        y_buttons = menu_y + menu_h - btn_clear_img.get_height() - 30

        # prioridad
        sortp_rect = btn_sortp_img.get_rect()
        sortp_rect.topleft = (start_x, y_buttons)
        self.ventana.blit(btn_sortp_img, sortp_rect.topleft)

        # deadline
        sortd_rect = btn_sortd_img.get_rect()
        sortd_rect.topleft = (sortp_rect.right + spacing, y_buttons)
        self.ventana.blit(btn_sortd_img, sortd_rect.topleft)

        # clear
        clear_rect = btn_clear_img.get_rect()
        clear_rect.topleft = (sortd_rect.right + spacing, y_buttons)
        self.ventana.blit(btn_clear_img, clear_rect.topleft)

        return pedidos, icon_rects, clear_rect, sortp_rect, sortd_rect
