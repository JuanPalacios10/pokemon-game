from abc import ABC
from src.pokemon.pokemon import Pokemon


class Trainer(ABC):
    def __init__(self, name: str, pokemon: list[Pokemon]):
        self.__current = 0
        self.__pokemon = pokemon
        self.__health = 100
        self.__name = name

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

    def get_pokemon(self) -> list[Pokemon]:
        return [
            pokemon
            for index, pokemon in enumerate(self.__pokemon)
            if index != self.__current
        ]

    def set_pokemon(self) -> None:
        self.__pokemon = self.get_pokemon()
        self.__set_current_pokemon()

    def __set_current_pokemon(self) -> None:
        if self.__current < len(self.__pokemon) - 1:
            self.__current += 1

    def is_current_pokemon_alive(self) -> bool:
        return self.__health > 0

    def is_alive(self) -> bool:
        return len(self.__pokemon) > 0


class Player(Trainer):
    def __init__(self, pokemon: list):
        super().__init__("Player", pokemon)


class Enemy(Trainer):
    def __init__(self, pokemon: list):
        super().__init__("Enemy", pokemon)

    def choose_attack(self):
        pass
