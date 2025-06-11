import pygame
import os
from src.combat.combat import Combat, CombatState


class CombatUI:
    def __init__(self, combat: Combat, imgs) -> None:
        self.combat = combat
        self.imgs = imgs
        self.screen_width = 900
        self.screen_height = 650
        self.running = True
        self.screen_battle_bg = None
        self.text_attack = ""

        self.sidebar_width = 80
        self.icon_size = 50

        self.pokeball_alive = self.load_pokeball_image("pokeball_color.png")
        self.pokeball_dead = self.load_pokeball_image("pokeball_gray.png")

        self.loaded_images = {}

        self.enemy_wait_time = 0
        self.enemy_turn_delay = 4000

        self.preload_images()

    def load_pokeball_image(self, filename: str) -> pygame.Surface:
        current_dir = os.path.dirname(__file__)
        image_path = os.path.join(current_dir, "..", "..", "assets", "img", filename)
        if os.path.exists(image_path):
            img = pygame.image.load(image_path).convert_alpha()
            return pygame.transform.scale(img, (self.icon_size, self.icon_size))
        else:
            raise FileNotFoundError(f"Pokeball image {filename} not found in assets.")

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

    def preload_images(self):
        for name, url in self.imgs.items():
            image = self.load_image_from_url(url)
            if image:
                self.loaded_images[name.lower()] = pygame.transform.scale(
                    image, (150, 150)
                )

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

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                self.check_attack_button_click(pos)

    def update_screen(self):
        self.screen.blit(self.screen_battle_bg, (0, 50))
        self.draw_player_sidebar()
        self.draw_enemy_sidebar()
        self.draw_battlefield_pokemons()
        self.draw_attack_panel()
        self.draw_text_panel()
        self.draw_health_bars()

        state = self.combat.get_state()
        if state == CombatState.ENEMY_TURN:
            self.handle_enemy_turn_delay()

    def handle_enemy_turn_delay(self):
        if self.enemy_wait_time == 0:
            # Recién entramos al turno de la IA, empezamos a contar
            self.enemy_wait_time = pygame.time.get_ticks()
        else:
            current_time = pygame.time.get_ticks()
            if current_time - self.enemy_wait_time >= self.enemy_turn_delay:
                self.enemy_turn()
                self.enemy_wait_time = 0  # Reiniciamos el temporizador

    def enemy_turn(self):
        attack, damage = self.combat.enemy_set_attack()
        self.text_attack = f"Ataque de IA: {attack} ha causado {damage} de daño."
        print(self.text_attack)

    def draw_text_panel(self):
        panel_height = 50
        panel_color = (220, 220, 220)
        pygame.draw.rect(
            self.screen, panel_color, (0, 0, self.screen_width, panel_height)
        )

        font = pygame.font.Font(None, 28)
        text_surface = font.render(self.text_attack, True, (0, 0, 0))
        self.screen.blit(text_surface, (20, 15))

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

    def draw_battlefield_pokemons(self):
        # Dibujar el pokémon del jugador
        player_pokemon = self.combat.get_info_player()["pokemon_name"].lower()
        if player_pokemon in self.loaded_images:
            self.screen.blit(self.loaded_images[player_pokemon], (200, 320))

        # Dibujar el pokémon enemigo
        enemy_pokemon = self.combat.get_info_enemy()["pokemon_name"].lower()
        if enemy_pokemon in self.loaded_images:
            self.screen.blit(self.loaded_images[enemy_pokemon], (550, 320))

    def draw_attack_panel(self):
        panel_height = 140
        panel_color = (245, 245, 245)
        pygame.draw.rect(
            self.screen,
            panel_color,
            (0, self.screen_height - panel_height, self.screen_width, panel_height),
        )

        # --- Título del turno actual ---
        font_title = pygame.font.Font(None, 36)

        state = self.combat.get_state()

        if state == CombatState.PLAYER_TURN:
            turn_text = "Turno actual: Player"
        elif state == CombatState.ENEMY_TURN:
            turn_text = "Turno actual: IA"
        elif state == CombatState.WINNER:
            turn_text = f"Ganador: {self.combat.get_winner()}"
        else:
            turn_text = "Preparando batalla..."

        title_surface = font_title.render(turn_text, True, (0, 0, 0))
        self.screen.blit(title_surface, (30, self.screen_height - panel_height + 10))

        # --- Dibujar botones sólo si es el turno del jugador ---
        if state.name == "PLAYER_TURN":
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

    def draw_health_bars(self):
        # --- Barra de vida del jugador ---
        info_player = self.combat.get_info_player()
        player_current_health = info_player["pokemon_health"]
        player_max_health = info_player["pokemon_max_health"]
        player_health_percentage = player_current_health / player_max_health

        # Barra completa
        pygame.draw.rect(self.screen, (0, 0, 0), (200, 300, 150, 15), border_radius=5)
        # Barra de vida
        pygame.draw.rect(
            self.screen,
            (50, 205, 50),
            (200, 300, int(150 * player_health_percentage), 15),
            border_radius=5,
        )

        # Texto de vida del jugador
        font = pygame.font.Font(None, 20)
        text = f"{player_current_health}/{player_max_health}"
        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(
            center=(200 + 75, 290)
        )  # Centrado encima de la barra
        self.screen.blit(text_surface, text_rect)

        # --- Barra de vida del enemigo ---
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

        # Texto de vida del enemigo
        text_enemy = f"{enemy_current_health}/{enemy_max_health}"
        text_surface_enemy = font.render(text_enemy, True, (0, 0, 0))
        text_rect_enemy = text_surface_enemy.get_rect(center=(550 + 75, 290))
        self.screen.blit(text_surface_enemy, text_rect_enemy)

    def load_image_from_url(self, url: str):
        import io
        from urllib.request import urlopen

        try:
            response = urlopen(url)
            image_data = io.BytesIO(response.read())
            return pygame.image.load(image_data).convert_alpha()
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    def check_attack_button_click(self, pos):
        for move_name, rect in self.attack_buttons:
            if rect.collidepoint(pos):
                print(f"Ataque seleccionado: {move_name}")
                # Aquí puedes llamar el método de ataque del combat:
                damage = self.combat.set_attack(move_name)
                self.text_attack = f"Ataque: {move_name} ha causado {damage} de daño."
                print(self.text_attack)
