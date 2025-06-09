from enum import Enum
from src.trainers.trainers import Enemy, Player, Trainer
from src.utils.effectiveness import effectiveness


class CombatState(Enum):
    START = 0
    PLAYER_TURN = 1
    ENEMY_TURN = 2
    WINNER = 3


class Combat:
    def __init__(self, player: Player, enemy: Enemy):
        self.__state = CombatState.START
        self.__players = (player, enemy)
        self.__current_attack = ""
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
        return self.__current_attack

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

    def __calculate_effectiveness(
        self, current_trainer: Trainer, next_trainer: Trainer
    ) -> float:
        efectivity = 0
        current_type_1 = current_trainer.get_current_pokemon().get_type_1()
        current_type_2 = current_trainer.get_current_pokemon().get_type_2()
        next_type_1 = next_trainer.get_current_pokemon().get_type_1()
        next_type_2 = next_trainer.get_current_pokemon().get_type_2()

        if current_type_2 is None and next_type_2 is None:
            efectivity = effectiveness.get(current_type_1, {}).get(next_type_1, 1.0)

        if current_type_2 is not None and next_type_2 is None:
            efectivity = effectiveness.get(current_type_1, {}).get(
                next_type_1, 1.0
            ) * effectiveness.get(current_type_2, {}).get(next_type_1, 1.0)

        if current_type_2 is None and next_type_2 is not None:
            efectivity = effectiveness.get(current_type_1, {}).get(
                next_type_1, 1.0
            ) * effectiveness.get(current_type_1, {}).get(next_type_2, 1.0)

        if current_type_2 is not None and next_type_2 is not None:
            type_attack = current_trainer.get_current_pokemon().get_move_type(
                move_name=self.__current_attack
            )
            efectivity = effectiveness.get(type_attack, {}).get(
                next_type_1, 1.0
            ) * effectiveness.get(type_attack, {}).get(next_type_2, 1.0)

        return efectivity

    def __calculate_damage(
        self, current_trainer: Trainer, next_trainer: Trainer
    ) -> int:
        level = 15
        damage = (
            (
                (((2 * level) // 5) + 2)
                * (
                    current_trainer.get_current_pokemon().get_damage(
                        move_name=self.__current_attack
                    )
                    // next_trainer.get_current_pokemon().get_defense()
                )
                // 50
            )
            + 2
        ) * self.__calculate_effectiveness(
            current_trainer=current_trainer, next_trainer=next_trainer
        )

        return int(damage)

    def set_attack(self, attack: str) -> int:
        self.__current_attack = attack
        current_trainer = self.__players[self.__turn]
        self.__next_turn()
        next_trainer = self.__players[self.__turn]

        damage = self.__calculate_damage(
            current_trainer=current_trainer, next_trainer=next_trainer
        )
        self.__set_damage_to_trainer(damage=damage, trainer=next_trainer)

        if not next_trainer.is_alive():
            self.__set_winner(winner=current_trainer.get_name())

        return damage

    def __set_damage_to_trainer(self, damage: int, trainer: Trainer) -> None:
        current_health = trainer.get_current_pokemon_health() - damage
        trainer.set_current_pokemon_health(health=current_health)

        if not trainer.is_current_pokemon_alive():
            trainer.set_pokemon()

    def enemy_choose_attack(self):
        pass
