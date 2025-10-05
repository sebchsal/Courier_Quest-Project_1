# Librerías principales
import pygame
import time
import sys 
from PIL import Image # Para manejar el gif del menú
from tools.camera import Camera # Cámara para seguir al jugador
from tools.render import Renderer # Renderizador de elementos gráficos
from objects.map import Mapa, map_data # Mapa y datos del mapa
from objects.jobs import (inicializar_pedidos, jobs_data, dibujar_pedidos,
    aceptar_pedido, verificar_entrega, expirar_pedido,
    cancelar_pedido, activos, pickups_disponibles) # Manejo de pedidos
from objects.weather import Weather, weather_data # Clima y datos del clima
from objects.player import Player, MovimientoFlechas # Jugador y estrategia de movimiento
from objects.building import detectar_bloques # Detección de edificios
from objects.road import detectar_calles # Detección de calles
from objects.park import detectar_parques # Detección de parques
from tools.clean_all import clean_all # Limpieza de archivos temporales
from tools.game_data import append_score_record, save_game_binary, load_game_binary, load_json, SCORES_PATH
from tools.score_queue import ScoreQueue

# Clase principal del juego
class Game:
    def __init__(self):
        # Limpiar archivos viejos
        summary = clean_all()
        if summary:
            print("Limpieza completada:")
            for base, removed in summary.items():
                print(f"  {base}: borrados {len(removed)} → {', '.join(removed)}")
                
        pygame.init()
        pygame.mixer.init()
        self.ANCHO, self.ALTO = 800, 600
        self.TILE_SIZE = 40
        self.GAME_DURATION = 10 * 60
        self.ventana = pygame.display.set_mode((self.ANCHO, self.ALTO))
        pygame.display.set_caption("Courier Quest")
        self.score_queue = ScoreQueue()
        self.name_input_text = ""
        self.cursor_visible = True
        self.cursor_timer = 0
        self.cursor_interval = 500

        # Datos iniciales
        self.mapa = Mapa(map_data)
        self.clima = Weather(weather_data)
        self.jugador = Player(100, 100, MovimientoFlechas(), self.TILE_SIZE, max_weight=5)
        
        # Buscar casilla de calle válida para iniciar
        start_x = start_y = 0
        found = False
        for y in range(self.mapa.height):
            for x in range(self.mapa.width):
                tile = self.mapa.tiles[y][x]
                if tile == "C":  # solo calles
                    if self.mapa.tiles[y][x] not in ("B", "P"):  # evitar edificios y parques
                        start_x, start_y = x, y
                        found = True
                        break
            if found:
                break
        start_px = start_x * self.TILE_SIZE
        start_py = start_y * self.TILE_SIZE
        self.jugador = Player(start_px, start_py, MovimientoFlechas(), self.TILE_SIZE, max_weight=5)
        
        # Detectar bloques, calles y parques
        self.bloques_edificios = detectar_bloques(self.mapa, self.TILE_SIZE, "images/building.png")
        self.bloques_calles = detectar_calles(self.mapa, self.TILE_SIZE, "images/road.jpg")
        self.bloques_parques = detectar_parques(self.mapa, self.TILE_SIZE, "images/park.png")
        
        # Cámara
        self.camara = Camera(self.ANCHO, self.ALTO, self.TILE_SIZE)
        
        # Fuentes
        self.fuente = pygame.font.SysFont("Arial", 18)
        self.fuente_grande = pygame.font.SysFont("Arial", 48, bold=True)

        # imágenes en directorio images
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
            "btn_pause": pygame.transform.scale(pygame.image.load("images/btnpause.png").convert_alpha(), (80, 80)),
            "btn_resume": pygame.transform.scale(pygame.image.load("images/btnresume.png").convert_alpha(), (150, 150)),
            "pause_logo": pygame.transform.scale(pygame.image.load("images/logopause.png").convert_alpha(), (300, 300)),
            "btn_newgame": pygame.transform.scale(pygame.image.load("images/btnnewgame.png").convert_alpha(), (170, 170)),
            "btn_exitgame": pygame.transform.scale(pygame.image.load("images/btnexitgame.png").convert_alpha(), (170, 170)),
            "menu_logo": pygame.transform.scale(pygame.image.load("images/gamelogo.png").convert_alpha(), (400, 400)),
            "victory": pygame.transform.scale(pygame.image.load("images/gamewin.png").convert_alpha(), (300, 300)),
            "btn_save": pygame.transform.scale(pygame.image.load("images/btnsave.png").convert_alpha(), (140, 140)),
            "btn_load": pygame.transform.scale(pygame.image.load("images/btnload.png").convert_alpha(), (140, 140)),
            "btn_score": pygame.transform.scale(pygame.image.load("images/btnscore.png").convert_alpha(), (140, 140)),
            "btn_scorelist": pygame.transform.scale(pygame.image.load("images/btnscorelist.png").convert_alpha(), (400, 400)),
            "byps": pygame.image.load("images/byps.png").convert_alpha(),
            "btn_save": pygame.transform.scale(pygame.image.load("images/btnsave.png").convert_alpha(), (140, 140)),
            "logoname": pygame.transform.scale(pygame.image.load("images/logoname.png").convert_alpha(), (400, 400)),
            "btn_howplay": pygame.transform.scale(pygame.image.load("images/btnhowplay.png").convert_alpha(), (140, 140)),
            "logohowplay": pygame.transform.scale(pygame.image.load("images/logohowplay.png").convert_alpha(), (250, 250)),
        }
        # sonidos en directorio sounds
        self.sonidos = {
            "menu": "sounds/arcade_Courier_Quest.mp3",
            "gameplay": "sounds/arcade_gameplay.mp3"
        }

        # Cargar frames del gif para el fondo animado del menú
        gif = Image.open("images/Pixel_Art_City.gif") # Abrir el gif
        self.menu_frames = [] # Lista para guardar los frames
        # Extraer frames del gif
        try:
            while True:  # Bucle para extraer cada frame
                frame = gif.copy().convert("RGBA")
                mode = frame.mode
                size = frame.size
                data = frame.tobytes()
                py_image = pygame.image.fromstring(data, size, mode).convert_alpha()
                self.menu_frames.append(py_image)
                gif.seek(len(self.menu_frames))  # siguiente frame
        except EOFError:
            pass
        self.current_frame = 0
        self.last_update = time.time()
        self.frame_delay = 0.1  # segundos por frame del gif
        self.renderer = Renderer(self.fuente, self.fuente_grande, self.imagenes,
                                 self.ventana, self.ANCHO, self.ALTO, self.TILE_SIZE)
        
        # Estado del juego
        self.estado_juego = "main_menu"
        self.modo_inventario = "priority"
        self.start_time = time.time()
        self.selected_packets = []
        self.boton_reiniciar = None
        self.boton_salir = None
        self.boton_pause = None
        self.boton_resume = None
        self.boton_newgame = None
        self.boton_exitgame = None
        self.show_howplay = False
        self.boton_howplay = None
        self.boton_exit_howplay = None
        inicializar_pedidos(jobs_data)
        
        # meta de ingresos 
        total_api_payout = sum(p["payout"] for p in jobs_data)
        self.goal_income = int(total_api_payout * 2) # meta
        self.jugador.goal_income = self.goal_income
        print(f"Meta de ingresos establecida: {self.goal_income}")
        self.reproducir_musica("menu")
    
    # Reproducir música de fondo
    def reproducir_musica(self, tipo):
        pygame.mixer.music.stop()
        if tipo == "menu":
            pygame.mixer.music.load(self.sonidos["menu"])
        elif tipo == "gameplay":
            pygame.mixer.music.load(self.sonidos["gameplay"])
        pygame.mixer.music.set_volume(0.3)  # volumen 
        pygame.mixer.music.play(-1)  # loop infinito
    
    # Reiniciar el juego
    def reset_game(self): 
        print("Reiniciando juego completamente...")
        self.start_time = time.time()
        self.clima = Weather(weather_data)

        # Reiniciar jugador desde posición inicial (en calle válida)
        start_x = start_y = 0
        found = False
        for y in range(self.mapa.height):
            for x in range(self.mapa.width):
                tile = self.mapa.tiles[y][x]
                if tile == "C" and tile not in ("B", "P"):
                    start_x, start_y = x, y
                    found = True
                    break
            if found:
                break
        start_px = start_x * self.TILE_SIZE
        start_py = start_y * self.TILE_SIZE
        self.jugador.x = start_px
        self.jugador.y = start_py
        self.jugador.stamina = 100
        self.jugador.reputation = 70
        self.jugador.total_payments = 0
        self.jugador.penalties = 0
        self.jugador.final_score = 0
        self.jugador.goal_income = self.goal_income
        self.jugador.inventory.clear_all()
        self.jugador.victory_reason = None
        
        # Reiniciar pedidos completamente
        inicializar_pedidos(jobs_data)
        
        # Restaurar estados y botones
        self.estado_juego = "playing"
        self.boton_reiniciar = None
        self.boton_salir = None
        self.boton_pause = None
        self.boton_resume = None
        self.boton_newgame = None
        self.boton_exitgame = None
        self.selected_packets = []

        # Música de juego
        self.reproducir_musica("gameplay")
 
    # Congelar puntaje final
    def freeze_score(self):
        # Calcular puntaje final
        pay_mult = 1.05 if self.jugador.reputation >= 90 else 1.0
        score_base = self.jugador.total_payments * pay_mult
        used_time = int(time.time() - self.start_time)
        time_remaining = max(0, self.GAME_DURATION - used_time)
        time_bonus = (time_remaining // 10) * 2 if time_remaining >= int(self.GAME_DURATION * 0.2) else 0
        self.jugador.final_score = int(score_base + time_bonus - self.jugador.penalties)
    
    # Puntaje final registrado
    def record_final_score(self):
        nombre = self.score_queue.peek() or (self.player_name or "Jugador")
        append_score_record(
            nombre=nombre,
            score=self.jugador.final_score,
            extra={"reputation": int(self.jugador.reputation)}
        )
        self.score_queue.dequeue()
        print(f"Puntaje registrado: {nombre} = {self.jugador.final_score}...")
    

    def get_serializable_state(self):
        jugador_data = {
            "x": self.jugador.x,
            "y": self.jugador.y,
            "stamina": self.jugador.stamina,
            "reputation": self.jugador.reputation,
            "total_payments": self.jugador.total_payments,
            "penalties": self.jugador.penalties,
            "final_score": self.jugador.final_score,
            "goal_income": getattr(self.jugador, "goal_income", 0),
            "victory_reason": getattr(self.jugador, "victory_reason", None),
            "inventory_items": [item.__dict__ for item in getattr(self.jugador.inventory, "items", [])]
        }

        state = {
            "jugador": jugador_data,
            "tiempo": time.time() - self.start_time,
            "cola": self.score_queue.to_list()
        }
        return state
    
    # restaura el juego al cargar
    def restore_game(self, data):
        j = data["jugador"]
        self.jugador.x = j.get("x", 0)
        self.jugador.y = j.get("y", 0)
        self.jugador.stamina = j.get("stamina", 100)
        self.jugador.reputation = j.get("reputation", 70)
        self.jugador.total_payments = j.get("total_payments", 0)
        self.jugador.penalties = j.get("penalties", 0)
        self.jugador.final_score = j.get("final_score", 0)
        self.jugador.goal_income = j.get("goal_income", 0)
        self.jugador.victory_reason = j.get("victory_reason", None)
        self.start_time = time.time() - data["tiempo"]

        cola = data.get("cola", [])
        self.score_queue = ScoreQueue()
        for nombre in cola:
            self.score_queue.enqueue(nombre)
        print("Partida restaurada correctamente...")
    
    # Bucle principal del juego
    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            dt = clock.tick(30) / 1000.0
            self.cursor_timer += dt
            if self.cursor_timer >= self.cursor_interval:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

            # Eventos 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Menú de inicio
                if self.estado_juego == "main_menu":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        # Si la ventana How to Play está abierta, solo responde a su botón
                        if self.show_howplay:
                            if self.boton_exit_howplay and self.boton_exit_howplay.collidepoint(event.pos):
                                self.show_howplay = False
                            # Ignorar otros clics mientras está abierta
                            continue
                        if self.boton_newgame and self.boton_newgame.collidepoint(event.pos):
                            self.estado_juego = "name_input"
                        elif self.boton_load and self.boton_load.collidepoint(event.pos):
                            data = load_game_binary()
                            if data:
                                self.restore_game(data)
                                self.estado_juego = "playing"
                                self.reproducir_musica("gameplay")
                            else:
                                print("No se encontró partida guardada...")
                        elif self.boton_score and self.boton_score.collidepoint(event.pos):
                            self.top_scores = load_json(SCORES_PATH, [])
                            self.estado_juego = "score_menu"
                        elif self.boton_exitgame and self.boton_exitgame.collidepoint(event.pos):
                            running = False
                        elif self.boton_howplay and self.boton_howplay.collidepoint(event.pos):
                            self.show_howplay = True  
                    
                         

                # Menu de ingresar nombre
                elif self.estado_juego == "name_input":
                    if event.type == pygame.KEYDOWN: 
                        if event.key == pygame.K_RETURN:
                            if self.name_input_text.strip():
                                self.player_name = self.name_input_text.strip()
                                self.score_queue.enqueue(self.player_name)
                                self.name_input_text = ""
                                self.reset_game()
                                self.estado_juego = "playing"
                                self.reproducir_musica("gameplay")
                        elif event.key == pygame.K_BACKSPACE:
                            self.name_input_text = self.name_input_text[:-1]
                        else:
                            if len(self.name_input_text) < 15 and event.unicode.isprintable():
                                self.name_input_text += event.unicode

                # Aceptar pedido o abrir inventario
                elif self.estado_juego == "playing":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_e:
                            tile_x, tile_y = self.jugador.x // self.TILE_SIZE, self.jugador.y // self.TILE_SIZE
                            aceptar_pedido(tile_x, tile_y, self.jugador)
                        if event.key == pygame.K_i:
                            self.estado_juego = "inventory_menu"
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.boton_pause and self.boton_pause.collidepoint(event.pos):
                            self.estado_juego = "paused"
                
                # Game Over
                elif self.estado_juego == "game_over":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_x, mouse_y = event.pos
                        if self.boton_reiniciar and self.boton_reiniciar.collidepoint(mouse_x, mouse_y):
                            self.reset_game()
                            self.estado_juego = "playing"
                        elif self.boton_salir and self.boton_salir.collidepoint(mouse_x, mouse_y):
                            self.estado_juego = "main_menu"
                            self.reproducir_musica("menu")
                
                # Victoria
                elif self.estado_juego == "victory":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_x, mouse_y = event.pos
                        # Botón Play Again
                        if self.boton_reiniciar and self.boton_reiniciar.collidepoint(mouse_x, mouse_y):
                            print("Reiniciando partida desde pantalla de victoria...")
                            self.reset_game()
                            self.jugador.victory_reason = None
                            self.estado_juego = "playing"
                            self.reproducir_musica("gameplay")
                        # Botón Exit
                        elif self.boton_salir and self.boton_salir.collidepoint(mouse_x, mouse_y):
                            print("Regresando al menú principal desde victoria...")
                            self.jugador.victory_reason = None
                            self.estado_juego = "main_menu"
                            self.boton_reiniciar = None
                            self.boton_salir = None
                            self.reproducir_musica("menu")
                
                # Menú de inventario
                elif self.estado_juego == "inventory_menu":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_p:
                            self.modo_inventario = "priority"
                        elif event.key == pygame.K_d:
                            self.modo_inventario = "deadline"
                        elif event.key == pygame.K_ESCAPE:
                            self.estado_juego = "playing"
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_x, mouse_y = event.pos
                        icon_rects, clear_rect, sortp_rect, sortd_rect = self.renderer.dibujar_menu_inventario(
                            self.jugador, self.modo_inventario, self.selected_packets)
                        if sortp_rect.collidepoint(mouse_x, mouse_y):
                            self.modo_inventario = "priority"
                        elif sortd_rect.collidepoint(mouse_x, mouse_y):
                            self.modo_inventario = "deadline"
                        for pedido, del_rect in icon_rects:
                            if del_rect.collidepoint(mouse_x, mouse_y):
                                self.jugador.inventory.remove_by_id(pedido.id)
                                cancelar_pedido(pedido, self.jugador)
                        if clear_rect.collidepoint(mouse_x, mouse_y):
                            for pedido in list(self.jugador.inventory.items):
                                cancelar_pedido(pedido, self.jugador)
                            self.jugador.inventory.clear_all()
                
                # Menú de pausa
                elif self.estado_juego == "paused":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.boton_resume and self.boton_resume.collidepoint(event.pos):
                            self.estado_juego = "playing"
                        elif self.boton_save and self.boton_save.collidepoint(event.pos):
                            state = self.get_serializable_state()
                            save_game_binary(state)
                            print("Partida guardada correctamente (serializable)...")
                            self.estado_juego = "main_menu"
                            self.reproducir_musica("menu")
                        elif self.boton_salir and self.boton_salir.collidepoint(event.pos):
                            self.estado_juego = "main_menu"
                            self.reproducir_musica("menu")
                
                # Menú de score list
                elif self.estado_juego == "score_menu":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.estado_juego = "main_menu"
            
            # Estados del juego
            # Menú de inicio
            if self.estado_juego == "main_menu":
                now = time.time()
                if now - self.last_update > self.frame_delay:
                    self.current_frame = (self.current_frame + 1) % len(self.menu_frames)
                    self.last_update = now
                self.boton_newgame, self.boton_exitgame, self.boton_load, self.boton_score, self.boton_howplay = \
                self.renderer.dibujar_menu_inicio(self.menu_frames[self.current_frame])
                if self.show_howplay:
                    self.boton_exit_howplay = self.renderer.dibujar_how_to_play()
            elif self.estado_juego == "name_input":
                self.renderer.dibujar_nombre(self.name_input_text, self.cursor_visible, self.imagenes["logoname"])
            
            # Juego en progreso
            elif self.estado_juego == "playing":
                teclas = pygame.key.get_pressed()
                self.clima.update()
                moved = self.jugador.mover(teclas, self.mapa, self.clima)
                if not moved:
                    tile_x = int(self.jugador.x // self.TILE_SIZE)
                    tile_y = int(self.jugador.y // self.TILE_SIZE)
                    self.jugador.recover(dt, resting=self.mapa.is_rest_point(tile_x, tile_y)
                    )

                tile_x, tile_y = self.jugador.x // self.TILE_SIZE, self.jugador.y // self.TILE_SIZE
                verificar_entrega(tile_x, tile_y, self.jugador, self.mapa)
                # Expiraciones de pedidos
                now = time.time()
                for pedido in list(activos):
                    try:
                        if pedido.accepted_time and now > pedido.accepted_time + 30:
                            expirar_pedido(pedido, self.jugador)
                    except Exception:
                        pass
                for pedido in list(pickups_disponibles):
                    try:
                        if hasattr(pedido, "deadline") and pedido.deadline:
                            deadline = float(pedido.deadline)
                            if now > deadline:
                                expirar_pedido(pedido, self.jugador)
                    except Exception:
                        pass

                # Calcular tiempo restante
                tiempo_restante = max(0, self.GAME_DURATION - int(time.time() - self.start_time))
                if hasattr(self.jugador, "goal_income") and self.jugador.final_score >= self.jugador.goal_income:
                    print("¡Meta alcanzada! Ventana de victoria...")
                    self.freeze_score()
                    self.record_final_score() 
                    self.estado_juego = "victory"
                    self.jugador.victory_reason = "income_goal"
                    pygame.mixer.music.stop()
                if tiempo_restante <= 0:
                    self.freeze_score()
                    self.record_final_score() 
                    self.estado_juego = "game_over"
                    pygame.mixer.music.stop()
                # Dibujar el juego completo (HUD + mundo)
                self.boton_pause = self.renderer.dibujar_juego(
                    self.jugador, self.mapa, self.clima,
                    self.bloques_calles, self.bloques_parques, self.bloques_edificios,
                    dibujar_pedidos, tiempo_restante, self.ANCHO, self.ALTO)
            
            # Menú de pausa 
            elif self.estado_juego == "paused":
                self.boton_resume, self.boton_salir, self.boton_save = self.renderer.dibujar_menu_pausa(
                self.jugador, self.mapa, self.bloques_calles,
                self.bloques_parques, self.bloques_edificios)
            
            # Game Over
            elif self.estado_juego == "game_over":
                self.boton_reiniciar, self.boton_salir = self.renderer.dibujar_menu_gameover(
                self.jugador, self.mapa, self.bloques_calles, self.bloques_parques,
                self.bloques_edificios)
            
            # Victoria
            elif self.estado_juego == "victory":
                self.boton_reiniciar, self.boton_salir = self.renderer.dibujar_menu_victoria(
                    self.jugador, self.mapa, self.bloques_calles, 
                    self.bloques_parques, self.bloques_edificios)
            
            # Inventario
            elif self.estado_juego == "inventory_menu":
                self.renderer.dibujar_menu_inventario(self.jugador, self.modo_inventario, self.selected_packets)
            elif self.estado_juego == "score_menu":
                self.renderer.dibujar_menu_score(self.top_scores)
                for event in pygame.event.get():
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.estado_juego = "main_menu"
            
            pygame.display.flip()
            clock.tick(30)
        
        pygame.mixer.music.stop()
        pygame.quit()
        sys.exit()