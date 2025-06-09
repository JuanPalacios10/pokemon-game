from abc import ABC
from src.pokemon.pokemon import Pokemon


class Trainer(ABC):
    def __init__(self, name: str, pokemon: list[Pokemon]):
        self.__current = 0
        self.__pokemon = pokemon
        self.__health = pokemon[0].get_hp()
        self.__name = name
        self.__is_alive = True

    def get_name(self) -> str:
        return self.__name

    def get_current_pokemon(self) -> Pokemon:
        return self.__pokemon[self.__current]

    def get_current_pokemon_health(self) -> int:
        return self.__health

    def set_current_pokemon_health(self, health: int) -> None:
        if health < 0:
            self.__health = 0
            return

        self.__health = health

    def get_live_pokemon(self) -> int:
        if not self.is_alive():
            return 0

        return len(self.__pokemon) - self.__current

    def set_pokemon(self) -> None:
        self.__set_current_pokemon()

        if not self.is_alive():
            return None

        self.__health = self.get_current_pokemon().get_hp()

    def __set_current_pokemon(self) -> None:
        if self.__current < len(self.__pokemon) - 1:
            self.__current += 1
            return

        self.__is_alive = False

    def is_current_pokemon_alive(self) -> bool:
        return self.__health > 0

    def is_alive(self) -> bool:
        return self.__is_alive


class Player(Trainer):
    def __init__(self, pokemon: list):
        super().__init__("Player", pokemon)


class Enemy(Trainer):
    def __init__(self, pokemon: list):
        super().__init__("Enemy", pokemon)

    def choose_attack(self):
        pass
