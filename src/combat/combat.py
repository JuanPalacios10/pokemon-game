from enum import Enum
import random
from typing import TYPE_CHECKING
from src.trainers.trainers import Player, Trainer
from src.utils.effectiveness import effectiveness

if TYPE_CHECKING:
    from src.trainers.enemy.ia import Enemy


class CombatState(Enum):
    """
    Enumeración que representa los posibles estados del combate.
    """

    START = 0
    PLAYER_TURN = 1
    ENEMY_TURN = 2
    WINNER = 3


class Combat:
    """
    Clase que gestiona el flujo y la lógica de un combate entre un jugador y un enemigo.

    Atributos:
        __state (CombatState): Estado actual del combate.
        __players (tuple[Player, Enemy]): Tupla con el jugador y el enemigo.
        __current_attack (str): Nombre del ataque actual.
        __winner (str | None): Nombre del ganador, si existe.
        DEFAULT_POKEMON_LEVEL (int): Nivel por defecto de los Pokémon en combate.
    """

    def __init__(self, player: Player, enemy: "Enemy"):
        """
        Inicializa el combate entre el jugador y el enemigo.

        Args:
            player (Player): Instancia del jugador.
            enemy (Enemy): Instancia del enemigo.
        """
        self.__state = CombatState.START
        self.__players = (player, enemy)
        self.__current_attack = ""
        self.__winner = None
        self.__next_turn()
        self.DEFAULT_POKEMON_LEVEL = 20

    def __next_turn(self) -> None:
        """
        Determina quién tiene el siguiente turno en función de la velocidad de los Pokémon activos.
        """
        # Se obtienen las velocidades de los Pokémon activos de cada jugador
        speed_pokemon_player = self.__players[0].get_current_pokemon().get_speed()
        speed_pokemon_enemy = self.__players[1].get_current_pokemon().get_speed()

        # Si el Pokémon del jugador es más rápido, el turno es del jugador
        if speed_pokemon_player > speed_pokemon_enemy:
            self.__turn = 0
            self.__state = CombatState.PLAYER_TURN
            return

        # Si el Pokémon enemigo es más rápido, el turno es del enemigo
        if speed_pokemon_player < speed_pokemon_enemy:
            self.__turn = 1
            self.__state = CombatState.ENEMY_TURN
            return

        # Si tienen la misma velocidad, el turno se decide aleatoriamente
        self.__turn = random.choice([0, 1])
        self.__state = (
            CombatState.PLAYER_TURN if self.__turn == 0 else CombatState.ENEMY_TURN
        )

    def get_players(self) -> tuple[Player, "Enemy"]:
        """
        Devuelve la tupla con el jugador y el enemigo.

        Returns:
            tuple[Player, Enemy]: Jugador y enemigo.
        """
        return self.__players

    def get_info_player(self):
        """
        Obtiene información relevante del jugador y su Pokémon activo.

        Returns:
            dict: Información del jugador y su Pokémon.
        """
        player_name = self.__players[0].get_name()
        current_pokemon = self.__players[0].get_current_pokemon()
        health = self.__players[0].get_current_pokemon_health()
        live_pokemon = self.__players[0].get_live_pokemon()

        return {
            "player_name": player_name,
            "pokemon_name": current_pokemon.get_name(),
            "pokemon_health": health,
            "pokemon_max_health": current_pokemon.get_hp(),
            "pokemon_attack_1": current_pokemon.get_move_1_name(),
            "pokemon_attack_2": current_pokemon.get_move_2_name(),
            "pokemon_super_attack": current_pokemon.get_super_move_name(),
            "live_pokemon": live_pokemon,
        }

    def get_info_enemy(self):
        """
        Obtiene información relevante del enemigo y su Pokémon activo.

        Returns:
            dict: Información del enemigo y su Pokémon.
        """
        enemy_name = self.__players[1].get_name()
        current_pokemon = self.__players[1].get_current_pokemon()
        health = self.__players[1].get_current_pokemon_health()
        live_pokemon = self.__players[1].get_live_pokemon()

        return {
            "enemy_name": enemy_name,
            "pokemon_name": current_pokemon.get_name(),
            "pokemon_health": health,
            "pokemon_max_health": current_pokemon.get_hp(),
            "live_pokemon": live_pokemon,
        }

    def get_state(self) -> CombatState:
        """
        Devuelve el estado actual del combate.

        Returns:
            CombatState: Estado del combate.
        """
        return self.__state

    def __next_trainer(self) -> None:
        """
        Cambia el turno al siguiente entrenador.
        """
        if self.__turn == 0:
            self.__turn = 1
            self.__state = CombatState.ENEMY_TURN
            return

        self.__turn = 0
        self.__state = CombatState.PLAYER_TURN

    def get_winner(self) -> str | None:
        """
        Devuelve el nombre del ganador si existe.

        Returns:
            str | None: Nombre del ganador o None si aún no hay ganador.
        """
        return self.__winner

    def set_winner(self, winner: str) -> None:
        """
        Establece el ganador del combate y cambia el estado a WINNER.

        Args:
            winner (str): Nombre del ganador.
        """
        self.__state = CombatState.WINNER
        self.__winner = winner

    def get_current_attack(self) -> str:
        """
        Devuelve el nombre del ataque actual.

        Returns:
            str: Nombre del ataque.
        """
        return self.__current_attack

    def set_current_attack(self, attack: str) -> None:
        """
        Establece el nombre del ataque actual.

        Args:
            attack (str): Nombre del ataque.
        """
        self.__current_attack = attack

    def calculate_effectiveness(
        self, current_trainer: Trainer, next_trainer: Trainer, attack: str
    ) -> float:
        """
        Calcula la efectividad del ataque según los tipos de los Pokémon.

        Args:
            current_trainer (Trainer): Entrenador que realiza el ataque.
            next_trainer (Trainer): Entrenador que recibe el ataque.
            attack (str): Nombre del ataque.

        Returns:
            float: Multiplicador de efectividad.
        """
        # Inicializa la efectividad en 0
        efectivity = 0
        # Obtiene los tipos del Pokémon actual y del siguiente (pueden ser uno o dos tipos)
        current_type_1 = current_trainer.get_current_pokemon().get_type_1()
        current_type_2 = current_trainer.get_current_pokemon().get_type_2()
        next_type_1 = next_trainer.get_current_pokemon().get_type_1()
        next_type_2 = next_trainer.get_current_pokemon().get_type_2()

        # Caso 1: ambos Pokémon tienen solo un tipo
        if current_type_2 is None and next_type_2 is None:
            efectivity = effectiveness.get(current_type_1, {}).get(next_type_1, 1.0)

        # Caso 2: el atacante tiene dos tipos y el defensor uno
        if current_type_2 is not None and next_type_2 is None:
            efectivity = effectiveness.get(current_type_1, {}).get(
                next_type_1, 1.0
            ) * effectiveness.get(current_type_2, {}).get(next_type_1, 1.0)

        # Caso 3: el atacante tiene un tipo y el defensor dos
        if current_type_2 is None and next_type_2 is not None:
            efectivity = effectiveness.get(current_type_1, {}).get(
                next_type_1, 1.0
            ) * effectiveness.get(current_type_1, {}).get(next_type_2, 1.0)

        # Caso 4: ambos tienen dos tipos, se usa el tipo del movimiento para calcular la efectividad
        if current_type_2 is not None and next_type_2 is not None:
            type_attack = current_trainer.get_current_pokemon().get_move_type(
                move_name=attack
            )
            efectivity = effectiveness.get(type_attack, {}).get(
                next_type_1, 1.0
            ) * effectiveness.get(type_attack, {}).get(next_type_2, 1.0)

        # Se retorna el valor final de la efectividad (puede ser 0.5, 1, 2, etc. según las tablas de tipos)
        return efectivity

    def calculate_damage(
        self, current_trainer: Trainer, next_trainer: Trainer, attack: str
    ) -> int:
        """
        Calcula el daño infligido por un ataque considerando nivel, ataque, defensa y efectividad.

        Args:
            current_trainer (Trainer): Entrenador que ataca.
            next_trainer (Trainer): Entrenador que recibe el ataque.
            attack (str): Nombre del ataque.

        Returns:
            int: Daño calculado.
        """
        # Se establece el nivel del Pokémon atacante (por defecto)
        level = self.DEFAULT_POKEMON_LEVEL

        # Fórmula de daño:
        # 1. Se calcula un factor base dependiente del nivel: (((2 * level) // 5) + 2)
        # 2. Se multiplica por el cociente entre el daño del atacante y la defensa del defensor
        # 3. Se divide el resultado entre 50 (// 50)
        # 4. Se suma 2 al resultado anterior
        # 5. Se multiplica por la efectividad del ataque (Segun los tipos de Pokémon)
        damage = (
            (
                (((2 * level) // 5) + 2)
                * (
                    current_trainer.get_current_pokemon().get_damage(move_name=attack)
                    // next_trainer.get_current_pokemon().get_defense()
                )
                // 50
            )
            + 2
        ) * self.calculate_effectiveness(
            current_trainer=current_trainer,
            next_trainer=next_trainer,
            attack=attack,
        )

        # Se retorna el daño final como entero
        return int(damage)

    def set_attack(self, attack: str) -> int:
        """
        Realiza un ataque, calcula el daño y aplica los efectos correspondientes.

        Args:
            attack (str): Nombre del ataque a realizar.

        Returns:
            int: Daño infligido al oponente.
        """
        # Se guarda el ataque actual seleccionado
        self.__current_attack = attack

        # Se obtiene el entrenador actual y el siguiente
        current_trainer = self.__players[self.__turn]
        self.__next_trainer()
        next_trainer = self.__players[self.__turn]

        # Se calcula el daño que el ataque actual causará al siguiente entrenador
        damage = self.calculate_damage(
            current_trainer=current_trainer,
            next_trainer=next_trainer,
            attack=self.__current_attack,
        )
        # Se aplica el daño al siguiente entrenador
        self.__set_damage_to_trainer(damage=damage, trainer=next_trainer)

        # Si el siguiente entrenador ya no tiene Pokémon vivos, se declara ganador al actual
        if not next_trainer.is_alive():
            self.set_winner(winner=current_trainer.get_name())

        # Se retorna el daño causado por el ataque
        return damage

    def __set_damage_to_trainer(self, damage: int, trainer: Trainer) -> None:
        """
        Aplica el daño al Pokémon activo del entrenador y gestiona el cambio de Pokémon si es necesario.

        Args:
            damage (int): Daño a aplicar.
            trainer (Trainer): Entrenador que recibe el daño.
        """
        # Se calcula la nueva vida del Pokémon actual del entrenador tras recibir el daño
        current_health = trainer.get_current_pokemon_health() - damage
        # Se establece la nueva vida del Pokémon activo
        trainer.set_current_pokemon_health(health=current_health)

        # Si el Pokémon actual ha sido derrotado, se selecciona el siguiente Pokémon y se pasa el turno
        if not trainer.is_current_pokemon_alive():
            trainer.set_pokemon()
            self.__next_turn()

    def enemy_set_attack(self) -> tuple[str, int]:
        """
        Permite que el enemigo elija y realice un ataque.

        Returns:
            tuple[str, int]: Nombre del ataque y daño infligido.
        """
        attack = self.__players[1].choose_attack(combat=self)
        return attack, self.set_attack(attack=attack)
