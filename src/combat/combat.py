from enum import Enum
from src.trainers.trainers import Enemy, Player, Trainer


class CombatState(Enum):
    START = 0
    PLAYER_TURN = 1
    ENEMY_TURN = 2
    WINNER = 3


class Combat:
    def __init__(self, player: Player, enemy: Enemy):
        self.__state = CombatState.START
        self.__players = (player, enemy)
        self.__current_atack = None
        self.__turn = 0
        self.__winner = None

    def get_info_player(self):
        player_name = self.__players[0].get_name()
        current_pokemon = self.__players[0].get_current_pokemon()
        health = self.__players[0].get_current_pokemon_health()

    def get_info_enemy(self):
        enemy_name = self.__players[1].get_name()
        current_pokemon = self.__players[1].get_current_pokemon()
        health = self.__players[1].get_current_pokemon_health()

    def get_state(self) -> CombatState:
        return self.__state

    def get_current_attack(self) -> str | None:
        return self.__current_atack

    def __next_turn(self) -> None:
        if self.__turn == 0:
            self.__turn = 1
            self.__state = CombatState.ENEMY_TURN
            return

        self.__turn = 0
        self.__state = CombatState.PLAYER_TURN

    def get_winner(self) -> str | None:
        return self.__winner

    def __set_winner(self, winner: str) -> None:
        self.__state = CombatState.WINNER
        self.__winner = winner

    def calculate_damage(self, attack: str) -> int:
        damage = 0
        self.__current_atack = attack
        current_trainer = self.__players[self.__turn]
        self.__next_turn()
        next_trainer = self.__players[self.__turn]

        self.__set_damage_to_trainer(damage=damage, trainer=next_trainer)

        if not next_trainer.is_alive():
            self.__set_winner(winner=current_trainer.get_name())

        return damage

    def __set_damage_to_trainer(self, damage: int, trainer: Trainer) -> None:
        current_health = trainer.get_current_pokemon_health() - damage
        trainer.set_current_pokemon_health(health=current_health)

        if not trainer.is_current_pokemon_alive():
            trainer.set_pokemon()

    def enmey_choose_attack(self):
        pass
