import pygame
import os
from src.combat.combat import Combat, CombatState


# Clase encargada de manejar la interfaz gráfica del combate
class CombatUI:
    def __init__(self, combat: Combat, imgs_loaded) -> None:
        # Guardamos el estado del combate y las imágenes precargadas
        self.combat = combat
        self.loaded_images = imgs_loaded
        self.screen_width = 900
        self.screen_height = 650
        self.running = True
        self.screen_battle_bg = None
        self.text_attack = ""

        # Configuración de la barra lateral
        self.sidebar_width = 80
        self.icon_size = 50

        # Cargamos las imágenes de pokeball (vivos y muertos)
        self.pokeball_alive = self.load_pokeball_image("pokeball_color.png")
        self.pokeball_dead = self.load_pokeball_image("pokeball_gray.png")

        # Control del tiempo de turno del enemigo (IA)
        self.enemy_wait_time = 0
        self.enemy_turn_delay = 4000

        # Control de mensajes de cambio de Pokémon
        self.change_message = ""
        self.show_change_message = False
        self.change_message_time = 0

    # Carga de imagen de Pokeball desde assets
    def load_pokeball_image(self, filename: str) -> pygame.Surface:
        current_dir = os.path.dirname(__file__)
        image_path = os.path.join(current_dir, "..", "..", "assets", "img", filename)
        if os.path.exists(image_path):
            img = pygame.image.load(image_path).convert_alpha()
            return pygame.transform.scale(img, (self.icon_size, self.icon_size))
        else:
            raise FileNotFoundError(f"Pokeball image {filename} not found in assets.")

    # Carga de imagen de fondo de batalla
    def load_battle_background(self, filename: str) -> pygame.Surface:
        current_dir = os.path.dirname(__file__)
        image_path = os.path.join(current_dir, "..", "..", "assets", "img", filename)
        if os.path.exists(image_path):
            img = pygame.image.load(image_path).convert()
            return pygame.transform.scale(
                img, (self.screen_width, self.screen_height - 140)
            )
        else:
            raise FileNotFoundError(f"Background image {filename} not found in assets.")

    # Loop principal de la UI
    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Combate Pokémon")
        self.screen_battle_bg = self.load_battle_background("battle_background.jpeg")
        clock = pygame.time.Clock()

        while self.running:
            self.handle_events()
            self.update_screen()
            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

    # Manejo de eventos (cerrar ventana, clics, etc.)
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                self.check_attack_button_click(pos)

    # Actualización completa de pantalla cada frame
    def update_screen(self):
        self.screen.blit(self.screen_battle_bg, (0, 50))
        self.draw_player_sidebar()
        self.draw_enemy_sidebar()
        self.draw_battlefield_pokemons()
        self.draw_attack_panel()
        self.draw_text_panel()
        self.draw_health_bars()

        if self.show_change_message:
            self.draw_change_message()

        state = self.combat.get_state()
        if state == CombatState.ENEMY_TURN:
            self.handle_enemy_turn_delay()

    # Lógica para generar retraso en el turno enemigo (para mostrar la animación)
    def handle_enemy_turn_delay(self):
        if self.enemy_wait_time == 0:
            self.enemy_wait_time = pygame.time.get_ticks()
        else:
            current_time = pygame.time.get_ticks()
            if current_time - self.enemy_wait_time >= self.enemy_turn_delay:
                self.enemy_turn()
                self.enemy_wait_time = 0

    # Ejecuta el turno del enemigo
    def enemy_turn(self):
        prev_player_pokemon = self.combat.get_info_player()["pokemon_name"]
        attack, damage = self.combat.enemy_set_attack()
        name_pokemon = self.combat.get_info_enemy()["pokemon_name"]
        self.text_attack = f"IA: {name_pokemon} ha utilizado el ataque {attack} y causó {damage} de daño."

        # Si cambia el Pokémon del jugador tras recibir daño
        current_player_pokemon = self.combat.get_info_player()["pokemon_name"]
        if prev_player_pokemon != current_player_pokemon:
            self.change_message = f"{prev_player_pokemon} fue debilitado! {current_player_pokemon} entra a la batalla!"
            self.show_change_message = True
            self.change_message_time = pygame.time.get_ticks()

        # print(self.text_attack)

    # Dibuja el mensaje de cambio de Pokémon temporalmente
    def draw_change_message(self):
        panel_height = 50
        panel_y = 50
        margin = 80
        panel_width = self.screen_width - (2 * margin)
        panel_color = (240, 240, 240)

        pygame.draw.rect(
            self.screen,
            panel_color,
            (margin, panel_y, panel_width, panel_height),
            border_radius=5,
        )
        pygame.draw.rect(
            self.screen,
            (180, 180, 180),
            (margin, panel_y, panel_width, panel_height),
            width=2,
            border_radius=5,
        )

        font = pygame.font.Font(None, 28)
        text_surface = font.render(self.change_message, True, (0, 0, 0))
        text_x = margin + (panel_width - text_surface.get_width()) // 2
        self.screen.blit(text_surface, (text_x, panel_y + 15))

        if pygame.time.get_ticks() - self.change_message_time > 4500:
            self.show_change_message = False

    # Panel superior con el texto de ataques recientes
    def draw_text_panel(self):
        panel_height = 50
        panel_color = (220, 220, 220)
        pygame.draw.rect(
            self.screen, panel_color, (0, 0, self.screen_width, panel_height)
        )
        font = pygame.font.Font(None, 28)
        text_surface = font.render(self.text_attack, True, (0, 0, 0))
        self.screen.blit(text_surface, (20, 15))

    # Barra lateral izquierda del jugador
    def draw_player_sidebar(self):
        panel_color = (230, 230, 250)
        pygame.draw.rect(
            self.screen,
            panel_color,
            (0, 50, self.sidebar_width, self.screen_height - 50),
        )

        live_count = self.combat.get_info_player()["live_pokemon"]

        for i in range(5):
            x, y = 15, 50 + 20 + i * (self.icon_size + 15)
            if i < live_count:
                self.screen.blit(self.pokeball_alive, (x, y))
            else:
                self.screen.blit(self.pokeball_dead, (x, y))

    # Barra lateral derecha del enemigo
    def draw_enemy_sidebar(self):
        panel_color = (250, 230, 230)
        pygame.draw.rect(
            self.screen,
            panel_color,
            (
                self.screen_width - self.sidebar_width,
                50,
                self.sidebar_width,
                self.screen_height - 50,
            ),
        )

        live_count = self.combat.get_info_enemy()["live_pokemon"]

        for i in range(5):
            x = self.screen_width - self.sidebar_width + 15
            y = 50 + 20 + i * (self.icon_size + 15)
            if i < live_count:
                self.screen.blit(self.pokeball_alive, (x, y))
            else:
                self.screen.blit(self.pokeball_dead, (x, y))

    # Dibuja los Pokémon actualmente en combate en el campo de batalla
    def draw_battlefield_pokemons(self):
        player_pokemon = self.combat.get_info_player()["pokemon_name"].lower()
        if player_pokemon in self.loaded_images:
            self.screen.blit(self.loaded_images[player_pokemon], (200, 320))

        enemy_pokemon = self.combat.get_info_enemy()["pokemon_name"].lower()
        if enemy_pokemon in self.loaded_images:
            self.screen.blit(self.loaded_images[enemy_pokemon], (550, 320))

    # Panel inferior con los botones de ataque
    def draw_attack_panel(self):
        panel_height = 140
        panel_color = (245, 245, 245)
        pygame.draw.rect(
            self.screen,
            panel_color,
            (0, self.screen_height - panel_height, self.screen_width, panel_height),
        )

        font_title = pygame.font.Font(None, 36)
        state = self.combat.get_state()

        if state == CombatState.PLAYER_TURN:
            turn_text = "Turno actual: Player"
        elif state == CombatState.ENEMY_TURN:
            turn_text = "Turno actual: IA, esta preparando su proximo ataque..."
        elif state == CombatState.WINNER:
            turn_text = f"Ganador: {self.combat.get_winner()}"
            self.text_attack = f"Ganador: {self.combat.get_winner()}"
        else:
            turn_text = "Preparando batalla..."

        title_surface = font_title.render(turn_text, True, (0, 0, 0))
        self.screen.blit(title_surface, (30, self.screen_height - panel_height + 10))

        # Dibujamos los botones de ataque solo en el turno del jugador
        if state == CombatState.PLAYER_TURN:
            moves = [
                self.combat.get_info_player()["pokemon_attack_1"],
                self.combat.get_info_player()["pokemon_attack_2"],
                self.combat.get_info_player()["pokemon_super_attack"],
            ]

            self.attack_buttons = []
            font = pygame.font.Font(None, 32)
            button_width = 250
            button_height = 50
            spacing_x = 40
            initial_x = 50
            y = self.screen_height - panel_height + 50

            for i, move_name in enumerate(moves):
                x = initial_x + i * (button_width + spacing_x)
                button_rect = pygame.Rect(x, y, button_width, button_height)
                pygame.draw.rect(
                    self.screen, (100, 149, 237), button_rect, border_radius=10
                )

                text_surface = font.render(move_name, True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=button_rect.center)
                self.screen.blit(text_surface, text_rect)

                self.attack_buttons.append((move_name, button_rect))
        else:
            self.attack_buttons = []

    # Barras de vida de ambos Pokémon
    def draw_health_bars(self):
        # Jugador
        info_player = self.combat.get_info_player()
        player_current_health = info_player["pokemon_health"]
        player_max_health = info_player["pokemon_max_health"]
        player_health_percentage = player_current_health / player_max_health

        pygame.draw.rect(self.screen, (0, 0, 0), (200, 300, 150, 15), border_radius=5)
        pygame.draw.rect(
            self.screen,
            (50, 205, 50),
            (200, 300, int(150 * player_health_percentage), 15),
            border_radius=5,
        )

        font = pygame.font.Font(None, 35)
        text = f"{player_current_health} / {player_max_health}"
        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(200 + 75, 280))
        self.screen.blit(text_surface, text_rect)

        # Enemigo
        info_enemy = self.combat.get_info_enemy()
        enemy_current_health = info_enemy["pokemon_health"]
        enemy_max_health = info_enemy["pokemon_max_health"]
        enemy_health_percentage = enemy_current_health / enemy_max_health

        pygame.draw.rect(self.screen, (0, 0, 0), (550, 300, 150, 15), border_radius=5)
        pygame.draw.rect(
            self.screen,
            (50, 205, 50),
            (550, 300, int(150 * enemy_health_percentage), 15),
            border_radius=5,
        )

        text_enemy = f"{enemy_current_health} / {enemy_max_health}"
        text_surface_enemy = font.render(text_enemy, True, (0, 0, 0))
        text_rect_enemy = text_surface_enemy.get_rect(center=(550 + 75, 280))
        self.screen.blit(text_surface_enemy, text_rect_enemy)

    # Detecta qué botón de ataque fue presionado
    def check_attack_button_click(self, pos):
        for move_name, rect in self.attack_buttons:
            if rect.collidepoint(pos):
                # print(f"Ataque seleccionado: {move_name}")

                prev_enemy_pokemon = self.combat.get_info_enemy()["pokemon_name"]

                damage = self.combat.set_attack(move_name)
                name_pokemon = self.combat.get_info_player()["pokemon_name"]
                self.text_attack = f"PLAYER: {name_pokemon} ha utilizado el ataque {move_name} y causó {damage} de daño."

                current_enemy_pokemon = self.combat.get_info_enemy()["pokemon_name"]
                if prev_enemy_pokemon != current_enemy_pokemon:
                    self.change_message = f"{prev_enemy_pokemon} fue debilitado! {current_enemy_pokemon} entra a la batalla!"
                    self.show_change_message = True
                    self.change_message_time = pygame.time.get_ticks()

                # print(self.text_attack)

