# Importamos todas las librerías necesarias
import pygame
import requests
import io
from urllib.request import urlopen

# Importamos módulos propios del proyecto
from src.dataset.dataset import Dataset
from src.pokemon.pokemon import Pokemon
from src.trainers.trainers import Player
from src.trainers.enemy.ia import Enemy
from src.combat.combat import Combat
from src.ui.combat_ui import CombatUI


# Clase que representa cada botón individual de selección de Pokémon en pantalla
class PokemonButton:
    def __init__(self, name: str, image: pygame.surface, rect: pygame.Rect):
        """
        Inicializa el botón del Pokémon.
        :param name: Nombre del Pokémon.
        :param image: Imagen del Pokémon (superficie pygame).
        :param rect: Rectángulo donde se dibuja el botón.
        """
        self.name = name
        self.image = pygame.transform.scale(image, (80, 80))  # Redimensionamos imagen
        self.rect = rect
        self.font = pygame.font.Font(None, 20)

    def draw(self, surface: pygame.surface) -> None:
        """
        Dibuja el botón en la pantalla.
        """
        border_color = (0, 0, 0)
        pygame.draw.rect(surface, border_color, self.rect, border_radius=5)
        inner_rect = self.rect.inflate(-5, -5)
        pygame.draw.rect(surface, (255, 255, 255), inner_rect, border_radius=5)
        surface.blit(self.image, (inner_rect.x + 10, inner_rect.y + 10))
        text = self.font.render(self.name.capitalize(), True, (0, 0, 0))
        surface.blit(text, (inner_rect.x + 5, inner_rect.y + 90))

    def is_clicked(self, pos: tuple[int, int]) -> bool:
        """
        Detecta si el botón fue clickeado.
        """
        return self.rect.collidepoint(pos)


# Clase encargada de descargar y cachear imágenes desde la PokeAPI
class ImageLoader:
    def __init__(self):
        """
        Inicializa el cargador de imágenes con caché para evitar llamadas duplicadas.
        """
        self.image_cache = {}  # Caché para URLs de imágenes
        self.surface_cache = {}  # Caché para superficies pygame ya cargadas

    def get_pokemon_image_url(self, pokemon_name: str) -> str | None:
        """
        Obtiene la URL de la imagen del Pokémon desde la PokeAPI.
        """
        pokemon_name = pokemon_name.lower()
        if pokemon_name in self.image_cache:
            return self.image_cache[pokemon_name]

        url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_name}/"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            image_url = data["sprites"]["front_default"]
            self.image_cache[pokemon_name] = image_url
            return image_url
        return None

    def load_image_from_url(self, url: str) -> pygame.Surface | None:
        """
        Descarga la imagen desde la URL y la convierte en superficie pygame.
        """
        try:
            response = urlopen(url)
            image_data = io.BytesIO(response.read())
            surface = pygame.image.load(image_data).convert_alpha()
            return surface
        except Exception as e:
            print(f"Error cargando imagen desde URL {url}: {e}")
            return None

    def get_scaled_image(
        self, pokemon_name: str, size: tuple[int, int]
    ) -> pygame.Surface | None:
        """
        Devuelve la imagen escalada al tamaño deseado, utilizando la caché si es posible.
        """
        pokemon_name = pokemon_name.lower()

        if pokemon_name in self.surface_cache:
            return pygame.transform.scale(self.surface_cache[pokemon_name], size)

        if pokemon_name in self.image_cache:
            url = self.image_cache[pokemon_name]
            surface = self.load_image_from_url(url)
            if surface:
                self.surface_cache[pokemon_name] = surface
                return pygame.transform.scale(surface, size)

        url = self.get_pokemon_image_url(pokemon_name)
        if url:
            surface = self.load_image_from_url(url)
            if surface:
                self.surface_cache[pokemon_name] = surface
                return pygame.transform.scale(surface, size)

        return None


# Clase principal de la pantalla de selección de los equipos
class PokemonSelectionScreen:
    def __init__(self):
        """
        Inicializa la pantalla de selección.
        """
        self.data = Dataset()
        self.image_loader = ImageLoader()
        self.name_pokemons = self.data.get_all_pokemon_names()
        self.pokemon_buttons = []
        self.current_selector = "player"  # Turno actual de selección
        self.select_player = []  # Pokémon seleccionados por el jugador
        self.select_ia = []  # Pokémon seleccionados por la IA

        # Parámetros de la ventana
        self.screen_width = 1000
        self.screen_height = 700
        self.bg_color = (255, 255, 255)
        self.running = True

    def run(self) -> None:
        """
        Bucle principal de la ventana.
        """
        pygame.init()
        self.font = pygame.font.Font(None, 36)
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Selecciona los Pokémons para la Batalla")
        clock = pygame.time.Clock()

        while self.running:
            self.handle_events()
            if self.running:
                self.update_screen()
                clock.tick(60)

        pygame.quit()

    def handle_events(self) -> None:
        """
        Maneja los eventos de la ventana (cerrar, clicks, etc).
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = pygame.mouse.get_pos()
                self.handle_mouse_click(pos)

    def handle_mouse_click(self, pos: tuple[int, int]) -> None:
        """
        Detecta qué botón fue presionado.
        """
        if self.switch_button.collidepoint(pos):
            self.switch_selector()
        elif self.battle_button.collidepoint(pos):
            self.confirm_selection()

        for button in self.pokemon_buttons:
            if button.is_clicked(pos):
                self.toggle_selection(button.name)
                break

    def toggle_selection(self, name: str) -> None:
        """
        Agrega o quita Pokémon de la selección actual.
        """
        selected_list = (
            self.select_player if self.current_selector == "player" else self.select_ia
        )

        if name in selected_list:
            selected_list.remove(name)
            # print(f"{name} eliminado de {self.current_selector}")
        elif (
            name not in self.select_player
            and name not in self.select_ia
            and len(selected_list) < 5
        ):
            selected_list.append(name)
            # print(f"{name} añadido a {self.current_selector}")

    def update_screen(self) -> None:
        """
        Actualiza/redibuja la pantalla.
        """
        self.screen.fill(self.bg_color)
        self.draw_buttons()
        self.draw_sidebar_panel()
        pygame.display.flip()

    def draw_buttons(self) -> None:
        """
        Dibuja todos los botones de selección de Pokémon.
        """
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
        """
        Dibuja el panel lateral con el estado actual.
        """
        self.draw_sidebar()
        self.draw_current_turn()
        self.draw_selected_teams()
        self.draw_action_buttons()

    def draw_sidebar(self) -> None:
        """
        Dibuja el fondo del panel lateral.
        """
        panel_x = 800
        panel_width = 200
        panel_color = (240, 240, 240)
        pygame.draw.rect(
            self.screen, panel_color, (panel_x, 0, panel_width, self.screen_height)
        )

    def draw_current_turn(self) -> None:
        """
        Muestra de quién es el turno actual.
        """
        panel_x = 800
        title = self.font.render("Turno de:", True, (0, 0, 0))
        selector = self.font.render(self.current_selector.upper(), True, (50, 50, 200))
        self.screen.blit(title, (panel_x + 20, 20))
        self.screen.blit(selector, (panel_x + 20, 60))

    def draw_selected_teams(self) -> None:
        """
        Muestra los Pokémon seleccionados por cada jugador.
        """
        panel_x = 800
        font_small = pygame.font.Font(None, 24)

        player_title = self.font.render("Player Team:", True, (0, 100, 0))
        ia_title = self.font.render("IA Team:", True, (150, 0, 0))
        self.screen.blit(player_title, (panel_x + 10, 110))
        self.screen.blit(ia_title, (panel_x + 10, 300))

        for i, name in enumerate(self.select_player):
            text = font_small.render(f"- {name.capitalize()}", True, (0, 0, 0))
            self.screen.blit(text, (panel_x + 20, 140 + i * 25))

        for i, name in enumerate(self.select_ia):
            text = font_small.render(f"- {name.capitalize()}", True, (0, 0, 0))
            self.screen.blit(text, (panel_x + 20, 330 + i * 25))

    def draw_action_buttons(self) -> None:
        """
        Dibuja los botones de acción: cambiar turno y comenzar batalla.
        """
        panel_x = 800

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

        self.battle_button = pygame.Rect(panel_x + 30, self.screen_height - 60, 140, 40)
        pygame.draw.rect(
            self.screen, (200, 50, 50), self.battle_button, border_radius=10
        )
        battle_text = self.font.render("¡Batalla!", True, (255, 255, 255))
        self.screen.blit(
            battle_text, battle_text.get_rect(center=self.battle_button.center)
        )

    def switch_selector(self) -> None:
        """
        Cambia de turno entre el jugador y la IA.
        """
        self.current_selector = "IA" if self.current_selector == "player" else "player"
        # print(f"Selector actual: {self.current_selector}")

    def load_imgs_pokemons(self):
        """
        Carga y escala las imágenes de los Pokémon seleccionados para el combate.
        """
        imagenes_loaded = {}
        target_size = (150, 150)
        for name in self.select_player + self.select_ia:
            image = self.image_loader.get_scaled_image(name, target_size)
            if image:
                imagenes_loaded[name.lower()] = image
            else:
                print(f"Advertencia: No se pudo cargar la imagen para {name}")
        return imagenes_loaded

    def confirm_selection(self) -> None:
        """
        Inicia el combate si ambos equipos tienen 5 Pokémon.
        """
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
            imgs_combat = self.load_imgs_pokemons()

            combat_ui = CombatUI(combat, imgs_loaded=imgs_combat)
            combat_ui.run()
        else:
            print("Debes seleccionar 5 Pokémon para cada jugador antes de continuar.")


# Ejecutamos la pantalla de selección solo si es el módulo principal
primera_pantalla = PokemonSelectionScreen()
if __name__ == "__main__":
    primera_pantalla.run()
    pygame.quit()
