import pygame
import requests
import io
from urllib.request import urlopen
from src.dataset.dataset import Dataset
from src.pokemon.pokemon import Pokemon
from src.trainers.trainers import Player
from src.trainers.enemy.ia import Enemy
from src.combat.combat import Combat
from src.ui.combat_ui import CombatUI


# clase para representar un botón de Pokémon
class PokemonButton:
    def __init__(self, name: str, image: pygame.surface, rect: pygame.Rect):
        self.name = name
        self.image = pygame.transform.scale(image, (80, 80))
        self.rect = rect
        self.font = pygame.font.Font(None, 20)

    def draw(self, surface: pygame.surface) -> None:
        border_color = (0, 0, 0)
        pygame.draw.rect(
            surface, border_color, self.rect, border_radius=5
        )  # Borde externo
        inner_rect = self.rect.inflate(-5, -5)  # Reduce el tamaño del rectángulo
        pygame.draw.rect(
            surface, (255, 255, 255), inner_rect, border_radius=5
        )  # Fondo interno

        surface.blit(self.image, (inner_rect.x + 10, inner_rect.y + 10))
        text = self.font.render(self.name.capitalize(), True, (0, 0, 0))
        surface.blit(text, (inner_rect.x + 5, inner_rect.y + 90))

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos)


# Clase para cargar imágenes de Pokémon desde la API de PokeAPI
class ImageLoader:
    def __init__(self):
        self.image_cache = {}

    def get_pokemon_image_url(self, pokemon_name: str) -> str | None:
        if pokemon_name in self.image_cache:
            return self.image_cache[pokemon_name]

        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name.lower()}/"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            image_url = data["sprites"]["front_default"]
            self.image_cache[pokemon_name] = image_url
            return image_url
        return None

    def load_image_from_url(self, url: str) -> pygame.Surface | None:
        try:
            response = urlopen(url)
            image_data = io.BytesIO(response.read())
            return pygame.image.load(image_data)
        except Exception as e:
            print(f"Error loading image from URL {url}: {e}")
            return None


# clase para manejar la pantalla de selección de Pokémon
class PokemonSelectionScreen:
    def __init__(self):
        self.data = Dataset()
        self.image_loader = ImageLoader()
        self.name_pokemons = self.data.get_all_pokemon_names()
        self.pokemon_buttons = []
        self.image_cache = {}
        self.current_selector = "player"
        self.select_player = []
        self.select_ia = []

        # Definición de dimensiones y colores
        self.screen_width = 1000
        self.screen_height = 700
        self.bg_color = (255, 255, 255)
        self.running = True

    def run(self) -> None:
        pygame.init()
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Selecciona los Pokémons para la Batalla")
        clock = pygame.time.Clock()

        while self.running:
            self.handle_events()
            self.update_screen()
            clock.tick(60)

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                self.handle_mouse_click(pos)

    def handle_mouse_click(self, pos: tuple[int, int]) -> None:
        if self.switch_button.collidepoint(pos):
            self.switch_selector()

        elif self.battle_button.collidepoint(pos):
            self.confirm_selection()

        # detectar click y delegar acciones
        for button in self.pokemon_buttons:
            if button.is_clicked(pos):
                self.toggle_selection(button.name)
                break

    def toggle_selection(self, name: str) -> None:
        selected_list = (
            self.select_player if self.current_selector == "player" else self.select_ia
        )

        if name in selected_list:
            selected_list.remove(name)
            print(f"{name} eliminado de {self.current_selector}")

        elif (
            name not in self.select_player
            and name not in self.select_ia
            and len(selected_list) < 5
        ):
            selected_list.append(name)
            print(f"{name} añadido a {self.current_selector}")

    def update_screen(self) -> None:
        self.screen.fill((self.bg_color))
        self.draw_buttons()
        self.draw_sidebar_panel()
        pygame.display.flip()

    def draw_buttons(self) -> None:
        x, y = 50, 50
        max_width = 800

        for i, name in enumerate(self.name_pokemons):
            if len(self.pokemon_buttons) <= i:
                url = self.image_loader.get_pokemon_image_url(name)
                image = self.image_loader.load_image_from_url(url) if url else None

                if image:
                    rect = pygame.Rect(x, y, 100, 120)
                    button = PokemonButton(name, image, rect)
                    self.pokemon_buttons.append(button)

            if i < len(self.pokemon_buttons):
                self.pokemon_buttons[i].draw(self.screen)
                x += 120
                if x + 100 > max_width:
                    x = 50
                    y += 150

    def draw_sidebar_panel(self) -> None:
        self.draw_sidebar()
        self.draw_current_turn()
        self.draw_selected_teams()
        self.draw_action_buttons()

    def draw_sidebar(self) -> None:
        panel_x = 800
        panel_width = 200
        panel_color = (240, 240, 240)
        pygame.draw.rect(
            self.screen, panel_color, (panel_x, 0, panel_width, self.screen_height)
        )

    def draw_current_turn(self) -> None:
        panel_x = 800
        title = self.font.render("Turno de:", True, (0, 0, 0))
        selector = self.font.render(self.current_selector.upper(), True, (50, 50, 200))
        self.screen.blit(title, (panel_x + 20, 20))
        self.screen.blit(selector, (panel_x + 20, 60))

    def draw_selected_teams(self) -> None:
        panel_x = 800
        font_small = pygame.font.Font(None, 24)

        # Títulos
        player_title = self.font.render("Player Team:", True, (0, 100, 0))
        ia_title = self.font.render("IA Team:", True, (150, 0, 0))
        self.screen.blit(player_title, (panel_x + 10, 110))
        self.screen.blit(ia_title, (panel_x + 10, 300))

        # Listado de seleccionados
        for i, name in enumerate(self.select_player):
            text = font_small.render(f"- {name.capitalize()}", True, (0, 0, 0))
            self.screen.blit(text, (panel_x + 20, 140 + i * 25))

        for i, name in enumerate(self.select_ia):
            text = font_small.render(f"- {name.capitalize()}", True, (0, 0, 0))
            self.screen.blit(text, (panel_x + 20, 330 + i * 25))

    def draw_action_buttons(self) -> None:
        panel_x = 800

        # Botón "Cambiar"
        self.switch_button = pygame.Rect(
            panel_x + 30, self.screen_height - 110, 140, 40
        )
        pygame.draw.rect(
            self.screen, (0, 150, 100), self.switch_button, border_radius=10
        )
        switch_text = self.font.render("Cambiar", True, (255, 255, 255))
        self.screen.blit(
            switch_text, switch_text.get_rect(center=self.switch_button.center)
        )

        # Botón "¡Batalla!"
        self.battle_button = pygame.Rect(panel_x + 30, self.screen_height - 60, 140, 40)
        pygame.draw.rect(
            self.screen, (200, 50, 50), self.battle_button, border_radius=10
        )
        battle_text = self.font.render("¡Batalla!", True, (255, 255, 255))
        self.screen.blit(
            battle_text, battle_text.get_rect(center=self.battle_button.center)
        )

    def switch_selector(self) -> None:
        if self.current_selector == "player":
            self.current_selector = "IA"
        elif self.current_selector == "IA":
            self.current_selector = "player"

        print(f"Selector actual: {self.current_selector}")

    def confirm_selection(self) -> None:
        if len(self.select_player) == 5 and len(self.select_ia) == 5:
            print("Selección confirmada, nos vamos a la batalla!")
            self.running = False

            player_pokemons = [
                Pokemon(self.data.get_pokemon_by_name(name))
                for name in self.select_player
            ]
            enemy_pokemons = [
                Pokemon(self.data.get_pokemon_by_name(name)) for name in self.select_ia
            ]

            player = Player(player_pokemons)
            enemy = Enemy(enemy_pokemons)

            combat = Combat(player, enemy)

            combat_ui = CombatUI(combat, imgs=self.image_loader.image_cache)
            combat_ui.run()
        else:
            print("Debes seleccionar 5 Pokémon para cada jugador antes de continuar.")


primera_pantalla = PokemonSelectionScreen()
if __name__ == "__main__":
    primera_pantalla.run()
    pygame.quit()
