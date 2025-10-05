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
    # Dibujar mapa
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
    # Dibujar juego completo
    def dibujar_juego(self, jugador, mapa, clima, bloques_calles, bloques_parques, bloques_edificios,
                      pedidos_activos, tiempo_restante, ancho, alto):
        # Calcular offsets de cámara
        offset_x, offset_y = jugador.x - ancho // 2, jugador.y - alto // 2
        max_offset_x = mapa.width * self.tile_size - ancho
        max_offset_y = mapa.height * self.tile_size - alto
        offset_x = max(0, min(offset_x, max_offset_x))
        offset_y = max(0, min(offset_y, max_offset_y))

        # Fondo blanco
        self.ventana.fill((255, 255, 255))

        # Dibujar mapa y objetos
        for c in bloques_calles: c.dibujar(self.ventana, offset_x, offset_y)
        for p in bloques_parques: p.dibujar(self.ventana, offset_x, offset_y)
        for b in bloques_edificios: b.dibujar(self.ventana, offset_x, offset_y)
        self.dibujar_mapa(mapa, offset_x, offset_y)
        jugador.dibujar(self.ventana, offset_x, offset_y)
        pedidos_activos(self.ventana, offset_x, offset_y, self.tile_size,
                        self.img["pickup"], self.img["dropoff"])

        # HUD superior: ciudad, clima y tiempo
        status = clima.get_status()
        minutos = tiempo_restante // 60
        segundos = tiempo_restante % 60
        texto = f"{mapa.cityname} | Clima: {status['condition']} | Tiempo: {minutos:02}:{segundos:02}"
        if status["next"]:
            texto += f" → {status['next']}"
        render_text = self.fuente.render(texto, True, (0, 0, 0))
        text_rect = render_text.get_rect(topleft=(10, 10))
        pygame.draw.rect(self.ventana, (255, 255, 255), text_rect.inflate(10, 6))
        pygame.draw.rect(self.ventana, (0, 0, 0), text_rect.inflate(10, 6), 1)
        self.ventana.blit(render_text, text_rect.topleft)

        # HUD reputación
        if jugador.reputation >= 90:
            rep_color = (0, 200, 0)
        elif jugador.reputation >= 50:
            rep_color = (200, 200, 0)
        else:
            rep_color = (200, 0, 0)
        rep_text = f"Reputación: {jugador.reputation}"
        render_rep = self.fuente.render(rep_text, True, rep_color)
        rep_rect = render_rep.get_rect(topleft=(10, text_rect.bottom + 5))
        pygame.draw.rect(self.ventana, (255, 255, 255), rep_rect.inflate(10, 6))
        pygame.draw.rect(self.ventana, (0, 0, 0), rep_rect.inflate(10, 6), 1)
        self.ventana.blit(render_rep, rep_rect.topleft)

        # HUD stamina
        barra_x = 10
        barra_y = alto - 40
        pygame.draw.rect(self.ventana, (200, 0, 0), (barra_x, barra_y, 200, 20))
        pygame.draw.rect(self.ventana, (0, 200, 0), (barra_x, barra_y, 2 * jugador.stamina, 20))
        estado = jugador.get_state()
        render_stamina = self.fuente.render(f"Stamina: {int(jugador.stamina)} ({estado})", True, (0, 0, 0))
        stamina_rect = render_stamina.get_rect(topleft=(10, barra_y - 20))
        pygame.draw.rect(self.ventana, (255, 255, 255), stamina_rect.inflate(10, 6))
        pygame.draw.rect(self.ventana, (0, 0, 0), stamina_rect.inflate(10, 6), 1)
        self.ventana.blit(render_stamina, stamina_rect.topleft)

        # HUD score (esquina inferior derecha)
        pay_mult = 1.05 if jugador.reputation >= 90 else 1.0
        score_base = jugador.total_payments * pay_mult
        score_now = score_base - jugador.penalties
        jugador.final_score = int(score_now)
        # Intentar obtener la meta desde jugador o game
        goal = getattr(jugador, "goal_income", None)
        if goal is None or goal <= 0:
            # Intenta obtenerla si fue asignada al objeto padre (por compatibilidad)
            if hasattr(self, "goal_income"):
                goal = getattr(self, "goal_income")
        # Texto del score
        if goal is not None and goal > 0:
            score_text = self.fuente.render(
                f"Score: {jugador.final_score}/{int(goal)}",True,(0, 0, 0))
        else:
            score_text = self.fuente.render(
                f"Score: {jugador.final_score}",True,(0, 0, 0))

        # Dibujar recuadro en esquina inferior derecha
        score_rect = score_text.get_rect(bottomright=(self.ancho - 10, self.alto - 10))
        pygame.draw.rect(self.ventana, (255, 255, 255), score_rect.inflate(10, 6))
        pygame.draw.rect(self.ventana, (0, 0, 0), score_rect.inflate(10, 6), 1)
        self.ventana.blit(score_text, score_rect.topleft)

        # Botón pausa en esquina superior derecha
        boton_pause = self.img["btn_pause"].get_rect()
        boton_pause.topright = (self.ancho - 10, 10)
        self.ventana.blit(self.img["btn_pause"], boton_pause.topleft)

        return boton_pause
    # Menú de inicio
    def dibujar_menu_inicio(self, frame_bg):
        # Fondo animado (un frame del gif escalado al tamaño de la ventana)
        bg = pygame.transform.scale(frame_bg, (self.ancho, self.alto))
        self.ventana.blit(bg, (0, 0))

        logo_x = self.ancho // 2 - self.img["menu_logo"].get_width() // 2
        logo_y = 5
        self.ventana.blit(self.img["menu_logo"], (logo_x, logo_y))

        # --- Botones principales ---
        boton_newgame = self.img["btn_newgame"].get_rect()
        boton_newgame.center = (self.ancho // 2, logo_y + 350)
        self.ventana.blit(self.img["btn_newgame"], boton_newgame.topleft)

        # Botón Load (izquierda)
        boton_load = self.img["btn_load"].get_rect()
        boton_load.center = (boton_newgame.left - 130, boton_newgame.centery)
        self.ventana.blit(self.img["btn_load"], boton_load.topleft)

        # Botón Score (derecha)
        boton_score = self.img["btn_score"].get_rect()
        boton_score.center = (boton_newgame.right + 130, boton_newgame.centery)
        self.ventana.blit(self.img["btn_score"], boton_score.topleft)

        # Botón Exit
        boton_exitgame = self.img["btn_exitgame"].get_rect()
        boton_exitgame.center = (self.ancho // 2, boton_newgame.bottom + 85)
        self.ventana.blit(self.img["btn_exitgame"], boton_exitgame.topleft)

        # Botón How to Play (esquina inferior izquierda)
        boton_howplay = self.img["btn_howplay"].get_rect()
        boton_howplay.bottomleft = (20, self.alto - 20) # margen de 20px
        self.ventana.blit(self.img["btn_howplay"], boton_howplay.topleft)

        # Firma de los integrantes
        byps_img = pygame.transform.scale(self.img["byps"], (150, 150))  # tamano reducido
        byps_rect = byps_img.get_rect()
        byps_rect.bottomright = (self.ancho - 10, self.alto - 20)  # margen de 20px
        self.ventana.blit(byps_img, byps_rect.topleft)

        return boton_newgame, boton_exitgame, boton_load, boton_score, boton_howplay
    
    # Dibujar menú de pausa
    def dibujar_menu_pausa(self, jugador, mapa, bloques_calles, bloques_parques, bloques_edificios):
        offset_x, offset_y = 0, 0
        # Dibujar mapa y jugador (escena congelada)
        for c in bloques_calles: c.dibujar(self.ventana, offset_x, offset_y)
        for p in bloques_parques: p.dibujar(self.ventana, offset_x, offset_y)
        for b in bloques_edificios: b.dibujar(self.ventana, offset_x, offset_y)
        self.dibujar_mapa(mapa, offset_x, offset_y)
        jugador.dibujar(self.ventana, offset_x, offset_y)

        # Fondo semitransparente
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.ventana.blit(overlay, (0, 0))

        # Logo de pausa
        logo_x = self.ancho // 2 - self.img["pause_logo"].get_width() // 2
        logo_y = 45
        self.ventana.blit(self.img["pause_logo"], (logo_x, logo_y))

        # Botón Resume
        boton_resume = self.img["btn_resume"].get_rect()
        boton_resume.center = (self.ancho // 2, logo_y + self.img["pause_logo"].get_height() - 50)
        self.ventana.blit(self.img["btn_resume"], boton_resume.topleft)

        # Botón Exit
        boton_salir = self.img["btn_exit"].get_rect()
        boton_salir.center = (self.ancho // 2, boton_resume.bottom + 150)
        self.ventana.blit(self.img["btn_exit"], boton_salir.topleft)

        # Botón Save
        boton_save = self.img["btn_save"].get_rect()
        boton_save.center = (self.ancho // 2, boton_resume.bottom + 40)
        self.ventana.blit(self.img["btn_save"], boton_save.topleft)

        return boton_resume, boton_salir, boton_save
    
    # Dibujar menú de game over
    def dibujar_menu_gameover(self, jugador, mapa, bloques_calles, bloques_parques, bloques_edificios):
        offset_x, offset_y = 0, 0
        for c in bloques_calles: c.dibujar(self.ventana, offset_x, offset_y)
        for p in bloques_parques: p.dibujar(self.ventana, offset_x, offset_y)
        for b in bloques_edificios: b.dibujar(self.ventana, offset_x, offset_y)
        self.dibujar_mapa(mapa, offset_x, offset_y)
        jugador.dibujar(self.ventana, offset_x, offset_y)

        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.ventana.blit(overlay, (0, 0))

        # Logo Game Over
        logo_x = self.ancho // 2 - self.img["gameover"].get_width() // 2
        logo_y = 45
        self.ventana.blit(self.img["gameover"], (logo_x, logo_y))

        # Mostrar score FINAL (congelado en game.py)
        score_text = self.fuente_grande.render(f"Score: {jugador.final_score}", True, (255, 255, 0))
        score_rect = score_text.get_rect(center=(self.ancho // 2, logo_y + self.img["gameover"].get_height() - 50))
        self.ventana.blit(score_text, score_rect)

        # Botón Play Again
        boton_reiniciar = self.img["btn_playagain"].get_rect()
        boton_reiniciar.center = (self.ancho // 2, logo_y + self.img["gameover"].get_height() + 40)
        self.ventana.blit(self.img["btn_playagain"], boton_reiniciar.topleft)

        # Botón Exit (vuelve a menú en game.py)
        boton_salir = self.img["btn_exit"].get_rect()
        boton_salir.center = (self.ancho // 2, boton_reiniciar.bottom + 60)
        self.ventana.blit(self.img["btn_exit"], boton_salir.topleft)

        return boton_reiniciar, boton_salir
    
    # Dibujar menú de victoria
    def dibujar_menu_victoria(self, jugador, mapa, bloques_calles, bloques_parques, bloques_edificios):
        offset_x, offset_y = 0, 0
        # Dibujar entorno estático
        for c in bloques_calles: c.dibujar(self.ventana, offset_x, offset_y)
        for p in bloques_parques: p.dibujar(self.ventana, offset_x, offset_y)
        for b in bloques_edificios: b.dibujar(self.ventana, offset_x, offset_y)
        self.dibujar_mapa(mapa, offset_x, offset_y)
        jugador.dibujar(self.ventana, offset_x, offset_y)

        # Fondo semitransparente oscuro
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.ventana.blit(overlay, (0, 0))

        # Imagen de victoria
        logo_x = self.ancho // 2 - self.img["victory"].get_width() // 2
        logo_y = 45
        self.ventana.blit(self.img["victory"], (logo_x, logo_y))

        # Mostrar el score final
        score_text = self.fuente_grande.render(f"Score: {jugador.final_score}", True, (255, 255, 0))
        score_rect = score_text.get_rect(center=(self.ancho // 2, logo_y + self.img["victory"].get_height() - 50))
        self.ventana.blit(score_text, score_rect)

        # Botón Play Again
        boton_reiniciar = self.img["btn_playagain"].get_rect()
        boton_reiniciar.center = (self.ancho // 2, score_rect.bottom + 40)
        self.ventana.blit(self.img["btn_playagain"], boton_reiniciar.topleft)

        # Botón Exit
        boton_salir = self.img["btn_exit"].get_rect()
        boton_salir.center = (self.ancho // 2, boton_reiniciar.bottom + 60)
        self.ventana.blit(self.img["btn_exit"], boton_salir.topleft)

        return boton_reiniciar, boton_salir
    
    # Dibujar menú de inventario
    def dibujar_menu_inventario(self, jugador, modo, selected_packets):
        # Elementos gráficos
        logo_img = self.img["logo"]
        btn_delete_img = self.img["btn_delete"]
        btn_clear_img = self.img["btn_clear"]
        btn_sortp_img = self.img["btn_sortp"]
        btn_sortd_img = self.img["btn_sortd"]
        pkg_img = self.img["pkg"]
        # Fondo semitransparente
        menu_w, menu_h = 750, 500
        menu_x = self.ancho // 2 - menu_w // 2
        menu_y = self.alto // 2 - menu_h // 2
        menu_rect = pygame.Rect(menu_x, menu_y, menu_w, menu_h)
        # Fondo del menú
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
        # Dibujar íconos de pedidos
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

        return icon_rects, clear_rect, sortp_rect, sortd_rect
    
    # Dibujar menú de score
    def dibujar_menu_score(self, top_scores):
        #Ventana Top 10 de puntajes
        overlay = pygame.Surface((self.ancho, self.alto))
        overlay.fill((0, 0, 0))
        self.ventana.blit(overlay, (0, 0))

        logo = self.img["btn_scorelist"]
        self.ventana.blit(logo, (self.ancho // 2 - logo.get_width() // 2, -50))

        start_y = 220
        for i, s in enumerate(top_scores[:10]):
            nombre = s.get("nombre", "Jugador")
            score = s.get("score", 0)
            txt = f"{i+1}. {nombre:<12} {score}"
            color = (255, 215, 0) if i == 0 else (255, 255, 255)
            surf = self.fuente.render(txt, True, color)
            rect = surf.get_rect(center=(self.ancho//2, start_y + i*30))
            self.ventana.blit(surf, rect)

        txt_exit = self.fuente.render("Press ESC to return", True, (200, 200, 200))
        rect_exit = txt_exit.get_rect(center=(self.ancho//2, self.alto - 50))
        self.ventana.blit(txt_exit, rect_exit)

    # Dibuja menu de ingresar el nombre
    def dibujar_nombre(self, texto, cursor_visible, img):
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.ventana.blit(overlay, (0, 0))
        self.ventana.blit(img, (self.ancho//2 - img.get_width()//2, 120))
        display_text = texto + ("|" if cursor_visible else "")
        text_surface = self.fuente.render(display_text, True, (255, 255, 0))
        self.ventana.blit(text_surface, (self.ancho//2 - text_surface.get_width()//2, 400))
        # donde se ingresa el nombre para la partida
        hint = self.fuente.render("Press ENTER to continue", True, (200, 200, 200))
        self.ventana.blit(hint, (self.ancho//2 - hint.get_width()//2, 450))
    
    # Dibujar ventana de instrucciones (How to Play)
    def dibujar_how_to_play(self):
        # Fondo oscuro semitransparente
        overlay = pygame.Surface((self.ancho, self.alto), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.ventana.blit(overlay, (0, 0))

        # Ventana central
        win_w, win_h = 600, 500
        win_x = (self.ancho - win_w) // 2
        win_y = (self.alto - win_h) // 2
        ventana_rect = pygame.Rect(win_x, win_y, win_w, win_h)
        pygame.draw.rect(self.ventana, (30, 30, 30), ventana_rect)
        pygame.draw.rect(self.ventana, (255, 255, 255), ventana_rect, 3)

        # Logo principal
        logo = self.img["logohowplay"]
        self.ventana.blit(logo, (win_x + win_w//2 - logo.get_width()//2, win_y - 60))

        # Texto explicativo
        texto = [
            "KEYS TO PLAY",
            "[W / UP] : go up",
            "[A / LEFT] : go left",
            "[S / DOWN] : go down",
            "[D / RIGHT] : go right",
            "[E] : accept a package",
            "[I] : open inventory",
            "",
            "INFO:",
            "Orders can be sorted and canceled from the inventory.",
            "To deliver it, look for the red symbol on the map",
            "and stand on top of it."
        ]
        y_offset = win_y + 130
        for line in texto:
            t = self.fuente.render(line, True, (255, 255, 255))
            self.ventana.blit(t, (win_x + 50, y_offset))
            y_offset += 30

        # Botón EXIT (esquina inferior derecha de la ventana principal)
        boton_exit = self.img["btn_exit"].get_rect()
        boton_exit.bottomright = (self.ancho - 110, self.alto - 50)  # esquina inferior derecha con margen
        self.ventana.blit(self.img["btn_exit"], boton_exit.topleft)

        return boton_exit
