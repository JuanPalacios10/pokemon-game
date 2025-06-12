import copy
from typing import TYPE_CHECKING, Callable
from src.trainers.trainers import Trainer

if TYPE_CHECKING:
    from src.combat.combat import Combat


class Enemy(Trainer):
    """
    Clase que representa a un entrenador enemigo controlado por IA.
    Implementa lógica de heurística y el algoritmo Minimax con poda alfa-beta
    para seleccionar el mejor ataque posible en combate.

    Métodos:
        evaluate_heuristic(combat: "Combat", maximizing: bool) -> float:
            Evalúa el estado actual del combate y retorna un valor heurístico.

        generate_possible_attacks(combat: "Combat", is_ia: bool) -> list[tuple[str, "Combat"]]:
            Genera todas las combinaciones posibles de ataques y sus estados resultantes.

        minmax(combat: "Combat", depth: int, alpha: float, beta: float, maximizing: bool) -> tuple[str | None, float]:
            Implementa el algoritmo Minimax con poda alfa-beta para determinar el mejor ataque.

        choose_attack(combat: "Combat") -> str:
            Selecciona el mejor ataque posible usando Minimax.
    """

    def __init__(self, pokemon: list):
        """
        Inicializa el entrenador enemigo con una lista de Pokémon.

        Args:
            pokemon (list): Lista de Pokémon del enemigo.
        """
        super().__init__("Enemy", pokemon)

    def evaluate_heuristic(self, combat: "Combat", maximizing: bool) -> float:
        """
        Evalúa el estado actual del combate y retorna un valor heurístico.

        Args:
            combat (Combat): Instancia del combate actual.
            maximizing (bool): Indica si se está maximizando o minimizando la heurística.

        Returns:
            float: Valor heurístico del estado del combate.
        """
        # Se obtienen los jugadores: player (usuario) y enemy (IA)
        player, enemy = combat.get_players()

        # Se obtiene la vida actual del Pokémon activo de cada entrenador
        hp_enemy = enemy.get_current_pokemon_health()
        hp_player = player.get_current_pokemon_health()

        # Se obtiene la cantidad de Pokémon vivos de cada entrenador
        live_pokemon_enemy = enemy.get_live_pokemon()
        live_pokemon_player = player.get_live_pokemon()

        # Se determina el entrenador actual y el siguiente según si se maximiza o minimiza
        # Si se maximiza, el estado del combate proviene de la elección del jugador, por eso el turno actual es del usuario
        # En caso contrario, el turno actual es de la IA
        current_trainer = player if maximizing else enemy
        next_trainer = enemy if maximizing else player

        # Se calcula la efectividad del ataque actual
        efectivity = combat.calculate_effectiveness(
            current_trainer=current_trainer,
            next_trainer=next_trainer,
            attack=combat.get_current_attack(),
        )

        # La heurística combina:
        # - Diferencia de vida entre la IA y el jugador
        # - Diferencia de Pokémon vivos (ponderado por 5)
        # - Efectividad del ataque (ponderado por 2)
        return (
            (hp_enemy - hp_player)
            + ((live_pokemon_enemy - live_pokemon_player) * 5)
            + (efectivity * 2)
        )

    def generate_possible_attacks(
        self, combat: "Combat", is_ia: bool
    ) -> list[tuple[str, "Combat"]]:
        """
        Genera todas las combinaciones posibles de ataques y sus estados resultantes.

        Args:
            combat (Combat): Instancia del combate actual.
            is_ia (bool): Indica si el turno es de la IA.

        Returns:
            list[tuple[str, Combat]]: Lista de tuplas con el nombre del ataque y el estado de combate resultante.
        """

        def set_attack(
            current_trainer: Trainer,
            next_trainer: Trainer,
            damage: int,
            combat: "Combat",
        ) -> None:
            current_health = next_trainer.get_current_pokemon_health() - damage
            next_trainer.set_current_pokemon_health(health=current_health)

            if not next_trainer.is_current_pokemon_alive():
                next_trainer.set_pokemon()

            if not next_trainer.is_alive():
                combat.set_winner(current_trainer.get_name())

        player, enemy = combat.get_players()
        current_trainer = enemy if is_ia else player
        next_trainer = player if is_ia else enemy
        attacks: list[tuple[str, "Combat"]] = []

        # Se obtienen los nombres de los movimientos disponibles del Pokémon actual
        moves: list[Callable[[], str]] = [
            current_trainer.get_current_pokemon().get_move_1_name,
            current_trainer.get_current_pokemon().get_move_2_name,
            current_trainer.get_current_pokemon().get_super_move_name,
        ]

        # Para cada movimiento posible, se simula el resultado del ataque
        for move in moves:
            # Se crea una copia profunda del estado actual del combate para no modificar el original
            copy_combat = copy.deepcopy(combat)
            player, enemy = copy_combat.get_players()
            current_trainer = enemy if is_ia else player
            next_trainer = player if is_ia else enemy
            attack = move()

            # Se calcula el daño que haría el ataque simulado
            damage = copy_combat.calculate_damage(
                current_trainer=current_trainer,
                next_trainer=next_trainer,
                attack=attack,
            )

            # Se registra el ataque y se actualiza el estado del combate simulado
            copy_combat.set_current_attack(attack=attack)
            set_attack(
                current_trainer=current_trainer,
                next_trainer=next_trainer,
                damage=damage,
                combat=copy_combat,
            )

            # Se añade la tupla (nombre del ataque, estado del combate simulado) a la lista de posibles ataques
            attacks.append((attack, copy_combat))

        return attacks

    def minmax(
        self, combat: "Combat", depth: int, alpha: float, beta: float, maximizing: bool
    ) -> tuple[str | None, float]:
        """
        Implementa el algoritmo Minimax con poda alfa-beta para determinar el mejor ataque.

        Args:
            combat (Combat): Instancia del combate actual.
            depth (int): Profundidad máxima de búsqueda.
            alpha (float): Valor alfa para la poda.
            beta (float): Valor beta para la poda.
            maximizing (bool): Indica si se está maximizando o minimizando.

        Returns:
            tuple[str | None, float]: Mejor ataque y su valor heurístico.
        """
        # Caso base: si se alcanza la profundidad máxima o hay un ganador, se evalúa la heurística del estado actual
        if depth == 0 or combat.get_winner():
            return None, self.evaluate_heuristic(combat=combat, maximizing=maximizing)

        best_move = None

        if maximizing:
            max_heuristic = float("-inf")

            # Para cada posible ataque de la IA, se simula el resultado y se llama recursivamente a minmax
            for move, new_combat in self.generate_possible_attacks(
                combat=combat, is_ia=True
            ):
                # Se explora el siguiente nivel del árbol, ahora minimizando (turno del jugador)
                _, heuristic = self.minmax(
                    combat=new_combat,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    maximizing=False,
                )

                # Se actualiza el mejor valor heurístico y el movimiento asociado si se encuentra uno mejor
                if heuristic > max_heuristic:
                    max_heuristic = heuristic
                    best_move = move

                # Se actualiza alpha con el mejor valor encontrado hasta ahora
                alpha = max(alpha, heuristic)

                # Poda alfa-beta: si beta es menor o igual a alpha, se corta la rama
                if beta <= alpha:
                    break

            return best_move, max_heuristic
        else:
            min_heuristic = float("inf")

            # Para cada posible ataque del jugador, se simula el resultado y se llama recursivamente a minmax
            for move, new_combat in self.generate_possible_attacks(
                combat=combat, is_ia=False
            ):
                # Se explora el siguiente nivel del árbol, ahora maximizando (turno de la IA)
                _, heuristic = self.minmax(
                    combat=new_combat,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    maximizing=True,
                )

                # Se actualiza el menor valor heurístico y el movimiento asociado si se encuentra uno peor para la IA
                if heuristic < min_heuristic:
                    min_heuristic = heuristic
                    best_move = move

                # Se actualiza beta con el mejor valor encontrado hasta ahora para el jugador
                beta = min(beta, heuristic)

                # Poda alfa-beta: si beta es menor o igual a alpha, se corta la rama
                if beta <= alpha:
                    break

            return best_move, min_heuristic

    def choose_attack(self, combat: "Combat") -> str:
        """
        Selecciona el mejor ataque posible usando el algoritmo Minimax.

        Args:
            combat (Combat): Instancia del combate actual.

        Returns:
            str: Nombre del ataque seleccionado.

        Raises:
            ValueError: Si no se encuentra un ataque válido.
        """
        attack, _ = self.minmax(
            combat=combat,
            depth=3,  # Se establece una profundidad de búsqueda de 3 niveles teniendo en cueta que el combate puede ser complejo y se busca un equilibrio entre rendimiento y dificultad
            alpha=float("-inf"),
            beta=float("inf"),
            maximizing=True,
        )

        if attack is None:
            raise ValueError("No valid attack found")

        return attack
