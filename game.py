import pygame, time, sys
from camera import Camera
from render import Renderer
from map import Mapa, map_data
from jobs import (inicializar_pedidos, jobs_data, dibujar_pedidos,
    aceptar_pedido, verificar_entrega, expirar_pedido,
    cancelar_pedido, activos, pickups_disponibles)
from weather import Weather, weather_data
from player import Player, MovimientoFlechas
from building import detectar_bloques
from road import detectar_calles
from park import detectar_parques

# Clase principal del juego
class Game:
    def __init__(self):
        pygame.init()
        self.ANCHO, self.ALTO = 800, 600
        self.TILE_SIZE = 40
        self.GAME_DURATION = 12 * 60
        self.ventana = pygame.display.set_mode((self.ANCHO, self.ALTO))
        pygame.display.set_caption("Courier Quest")

        # Datos iniciales
        self.mapa = Mapa(map_data)
        self.clima = Weather(weather_data)
        self.jugador = Player(100, 100, MovimientoFlechas(), self.TILE_SIZE, max_weight=5)

        self.bloques_edificios = detectar_bloques(self.mapa, self.TILE_SIZE, "images/building.png")
        self.bloques_calles = detectar_calles(self.mapa, self.TILE_SIZE, "images/road.jpg")
        self.bloques_parques = detectar_parques(self.mapa, self.TILE_SIZE, "images/park.png")

        self.camara = Camera(self.ANCHO, self.ALTO, self.TILE_SIZE)

        self.fuente = pygame.font.SysFont("Arial", 18)
        self.fuente_grande = pygame.font.SysFont("Arial", 48, bold=True)

        # imágenes en diccionario
        self.imagenes = {
            "logo": pygame.transform.scale(pygame.image.load("images/inventorylogo.png").convert_alpha(), (200, 200)),
            "btn_delete": pygame.transform.scale(pygame.image.load("images/btndelete.png").convert_alpha(), (80, 80)),
            "btn_clear": pygame.transform.scale(pygame.image.load("images/btnclear.png").convert_alpha(), (120, 120)),
            "pkg": pygame.transform.scale(pygame.image.load("images/pckup.png").convert_alpha(), (60, 60)),
            "btn_sortp": pygame.transform.scale(pygame.image.load("images/sortp.png").convert_alpha(), (120, 120)),
            "btn_sortd": pygame.transform.scale(pygame.image.load("images/sortd.png").convert_alpha(), (120, 120)),
            "gameover": pygame.transform.scale(pygame.image.load("images/gameover.png").convert_alpha(), (300, 300)),
            "btn_exit": pygame.transform.scale(pygame.image.load("images/btnexit.png").convert_alpha(), (150, 150)),
            "btn_playagain": pygame.transform.scale(pygame.image.load("images/playagain.png").convert_alpha(), (150, 150)),
            "pickup": pygame.transform.scale(pygame.image.load("images/pckup.png").convert_alpha(), (40, 40)),
            "dropoff": pygame.transform.scale(pygame.image.load("images/drop.png").convert_alpha(), (40, 40)),
        }

        self.renderer = Renderer(self.fuente, self.fuente_grande, self.imagenes,
                                 self.ventana, self.ANCHO, self.ALTO, self.TILE_SIZE)

        self.estado_juego = "playing"
        self.modo_inventario = "priority"
        self.start_time = time.time()
        self.selected_packets = []
        self.boton_reiniciar = None
        self.boton_salir = None
        inicializar_pedidos(jobs_data)
    # Reiniciar el juego
    def reset_game(self): 
        self.start_time = time.time()
        self.clima = Weather(weather_data)
        self.jugador = Player(100, 100, MovimientoFlechas(), self.TILE_SIZE, max_weight=5)
        inicializar_pedidos(jobs_data)
    # Bucle principal del juego
    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            dt = clock.get_time() / 1000.0

            # Eventos 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # Aceptar pedido
                if self.estado_juego == "playing":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_e:
                            tile_x, tile_y = self.jugador.x // self.TILE_SIZE, self.jugador.y // self.TILE_SIZE
                            aceptar_pedido(tile_x, tile_y, self.jugador)
                        if event.key == pygame.K_i:
                            self.estado_juego = "inventory_menu"
                # Game Over
                elif self.estado_juego == "game_over":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_x, mouse_y = event.pos
                        if self.boton_reiniciar and self.boton_reiniciar.collidepoint(mouse_x, mouse_y):
                            self.reset_game()
                            self.estado_juego = "playing"
                        elif self.boton_salir and self.boton_salir.collidepoint(mouse_x, mouse_y):
                            running = False
                # Menú de inventario
                elif self.estado_juego == "inventory_menu":
                    # Cambiar modo de inventario o salir
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p:
                            self.modo_inventario = "priority"
                        elif event.key == pygame.K_d:
                            self.modo_inventario = "deadline"
                        elif event.key == pygame.K_ESCAPE:
                            self.estado_juego = "playing"
                    # Clic del mouse
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_x, mouse_y = event.pos
                        pedidos, icon_rects, clear_rect, sortp_rect, sortd_rect = self.renderer.dibujar_menu_inventario(
                            self.jugador, self.modo_inventario, self.selected_packets)
                        # Cambiar modo de inventario
                        if sortp_rect.collidepoint(mouse_x, mouse_y):
                            self.modo_inventario = "priority"
                        elif sortd_rect.collidepoint(mouse_x, mouse_y):
                            self.modo_inventario = "deadline"
                        
                        for pedido, rect, del_rect in icon_rects:
                            if del_rect.collidepoint(mouse_x, mouse_y):
                                self.jugador.inventory.remove_by_id(pedido.id)
                                cancelar_pedido(pedido, self.jugador)

                        if clear_rect.collidepoint(mouse_x, mouse_y):
                            for pedido in list(self.jugador.inventory.items):
                                cancelar_pedido(pedido, self.jugador)
                            self.jugador.inventory.clear_all()

            # Juego en curso
            if self.estado_juego == "playing":
                teclas = pygame.key.get_pressed() # estado de teclas
                self.clima.update() # actualizar clima
                moved = self.jugador.mover(teclas, self.mapa, self.clima) # mover jugador
                # Recuperar stamina si no se movió
                if not moved:
                    tile_x = int(self.jugador.x // self.TILE_SIZE)
                    tile_y = int(self.jugador.y // self.TILE_SIZE)
                    self.jugador.recover(dt, resting=self.mapa.is_rest_point(tile_x, tile_y))
                # Verificar entregas
                tile_x, tile_y = self.jugador.x // self.TILE_SIZE, self.jugador.y // self.TILE_SIZE
                verificar_entrega(tile_x, tile_y, self.jugador, self.mapa)
                # Verificar expiración de pedidos
                now = time.time()
                for pedido in list(activos):
                    try:
                        if pedido.accepted_time and now > pedido.accepted_time + 30:
                            expirar_pedido(pedido, self.jugador)
                    except Exception as e:
                        print(f"⚠️ Error verificando expiración de {pedido.id}: {e}")
                # Verificar expiración de pickups
                for pedido in list(pickups_disponibles):
                    try:
                        if hasattr(pedido, "deadline") and pedido.deadline:
                            deadline = float(pedido.deadline)
                            if now > deadline:
                                expirar_pedido(pedido, self.jugador)
                    except Exception as e:
                        print(f"⚠️ Error verificando expiración de {pedido.id}: {e}")

                offset_x, offset_y = self.camara.calcular_offset(self.jugador, self.mapa)
                self.ventana.fill((255, 255, 255))
                # Dibujar calles, parques y edificios
                for c in self.bloques_calles: c.dibujar(self.ventana, offset_x, offset_y)
                for p in self.bloques_parques: p.dibujar(self.ventana, offset_x, offset_y)
                for b in self.bloques_edificios: b.dibujar(self.ventana, offset_x, offset_y)
                # Dibujar mapa y jugador
                self.renderer.dibujar_mapa(self.mapa, offset_x, offset_y)
                self.jugador.dibujar(self.ventana, offset_x, offset_y)
                dibujar_pedidos(self.ventana, offset_x, offset_y, self.TILE_SIZE,
                                self.imagenes["pickup"], self.imagenes["dropoff"])
                # HUD
                status = self.clima.get_status()
                tiempo_restante = max(0, self.GAME_DURATION - int(time.time() - self.start_time))
                if tiempo_restante <= 0:
                    self.estado_juego = "game_over"

                minutos = tiempo_restante // 60
                segundos = tiempo_restante % 60
                tiempo_txt = f"Tiempo: {minutos:02}:{segundos:02}"

                texto = (f"{self.mapa.cityname} | Clima: {status['condition']} | {tiempo_txt}")
                if status["next"]:
                    texto += f" → {status['next']}"

                render_text = self.fuente.render(texto, True, (0, 0, 0))
                text_rect = render_text.get_rect(topleft=(10, 10))
                # Reputación con color
                if self.jugador.reputation >= 90:
                    rep_color = (0, 200, 0)
                elif self.jugador.reputation >= 50:
                    rep_color = (200, 200, 0)
                else:
                    rep_color = (200, 0, 0)
                # Texto de reputación
                rep_text = f"Reputación: {self.jugador.reputation}"
                render_rep = self.fuente.render(rep_text, True, rep_color)
                rep_rect = render_rep.get_rect(topleft=(10, text_rect.bottom + 5))
                pygame.draw.rect(self.ventana, (255, 255, 255), rep_rect.inflate(10, 6))
                pygame.draw.rect(self.ventana, (0, 0, 0), rep_rect.inflate(10, 6), 1)
                self.ventana.blit(render_rep, rep_rect.topleft)
                # Fondo del texto principal
                pygame.draw.rect(self.ventana, (255, 255, 255), text_rect.inflate(10, 6))
                pygame.draw.rect(self.ventana, (0, 0, 0), text_rect.inflate(10, 6), 1)
                self.ventana.blit(render_text, text_rect.topleft)
                # Barra de stamina
                barra_x = 10
                barra_y = self.ALTO - 40
                pygame.draw.rect(self.ventana, (200, 0, 0), (barra_x, barra_y, 200, 20))
                pygame.draw.rect(self.ventana, (0, 200, 0), (barra_x, barra_y, 2 * self.jugador.stamina, 20))
                estado = self.jugador.get_state()
                # Texto de stamina
                render_stamina = self.fuente.render(f"Stamina: {int(self.jugador.stamina)} ({estado})", True, (0, 0, 0))
                stamina_rect = render_stamina.get_rect(topleft=(10, barra_y - 20))
                pygame.draw.rect(self.ventana, (255, 255, 255), stamina_rect.inflate(10, 6))
                pygame.draw.rect(self.ventana, (0, 0, 0), stamina_rect.inflate(10, 6), 1)
                self.ventana.blit(render_stamina, stamina_rect.topleft)

            # Game Over
            elif self.estado_juego == "game_over":
                offset_x, offset_y = self.camara.calcular_offset(self.jugador, self.mapa)
                # Dibujar calles, parques y edificios
                self.ventana.fill((255, 255, 255))
                for c in self.bloques_calles: c.dibujar(self.ventana, offset_x, offset_y)
                for p in self.bloques_parques: p.dibujar(self.ventana, offset_x, offset_y)
                for b in self.bloques_edificios: b.dibujar(self.ventana, offset_x, offset_y)
                # Dibujar mapa y jugador
                self.renderer.dibujar_mapa(self.mapa, offset_x, offset_y)
                self.jugador.dibujar(self.ventana, offset_x, offset_y)
                # Overlay
                overlay = pygame.Surface((self.ANCHO, self.ALTO), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.ventana.blit(overlay, (0, 0))
                # Cálculo de score final
                pay_mult = 1.05 if self.jugador.reputation >= 90 else 1.0
                score_base = self.jugador.total_payments * pay_mult
                used_time = int(time.time() - self.start_time)
                time_remaining = max(0, self.GAME_DURATION - used_time)
                time_bonus = 0
                if time_remaining >= self.GAME_DURATION * 0.2:
                    time_bonus = (time_remaining // 10) * 2
                score_final = score_base + time_bonus - self.jugador.penalties
                self.jugador.final_score = int(score_final)
                # Mostrar texto de Game Over
                logo_x = self.ANCHO // 2 - self.imagenes["gameover"].get_width() // 2
                logo_y = 45
                self.ventana.blit(self.imagenes["gameover"], (logo_x, logo_y))
                # Mostrar puntaje final
                score_text = self.fuente_grande.render(f"Score: {self.jugador.final_score}", True, (255, 255, 0))
                score_rect = score_text.get_rect(center=(self.ANCHO // 2, logo_y + self.imagenes["gameover"].get_height() - 50))
                self.ventana.blit(score_text, score_rect)
                # Botones   
                self.boton_reiniciar = self.imagenes["btn_playagain"].get_rect()
                self.boton_reiniciar.center = (self.ANCHO // 2, logo_y + self.imagenes["gameover"].get_height() + 40)
                self.ventana.blit(self.imagenes["btn_playagain"], self.boton_reiniciar.topleft)
                # Botón de salir
                self.boton_salir = self.imagenes["btn_exit"].get_rect()
                self.boton_salir.center = (self.ANCHO // 2, self.boton_reiniciar.bottom + 60)
                self.ventana.blit(self.imagenes["btn_exit"], self.boton_salir.topleft)

            # Inventario
            elif self.estado_juego == "inventory_menu":
                self.renderer.dibujar_menu_inventario(self.jugador, self.modo_inventario, self.selected_packets)

            pygame.display.flip()  # Actualizar pantalla
            clock.tick(30) # 30 FPS

        pygame.quit() # Cerrar Pygame
        sys.exit() # Salir del sistema
