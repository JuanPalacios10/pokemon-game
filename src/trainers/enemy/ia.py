import copy
from typing import TYPE_CHECKING, Callable
from src.trainers.trainers import Trainer

if TYPE_CHECKING:
    from src.combat.combat import Combat


class Enemy(Trainer):
    def __init__(self, pokemon: list):
        super().__init__("Enemy", pokemon)

    def evaluate_heuristic(self, combat: "Combat") -> float:
        player, enemy = combat.get_players()

        hp_enemy = enemy.get_current_pokemon_health()
        hp_player = player.get_current_pokemon_health()

        live_pokemon_enemy = enemy.get_live_pokemon()
        live_pokemon_player = player.get_live_pokemon()

        effectivity_move_1 = combat.calculate_effectiveness(
            current_trainer=enemy,
            next_trainer=player,
            attack=enemy.get_current_pokemon().get_move_1_name(),
        )
        effectivity_move_2 = combat.calculate_effectiveness(
            current_trainer=enemy,
            next_trainer=player,
            attack=enemy.get_current_pokemon().get_move_2_name(),
        )
        effectivity_move_3 = combat.calculate_effectiveness(
            current_trainer=enemy,
            next_trainer=player,
            attack=enemy.get_current_pokemon().get_super_move_name(),
        )

        best_effectivity = max(
            effectivity_move_1, effectivity_move_2, effectivity_move_3
        )

        return (
            (hp_enemy - hp_player)
            + ((live_pokemon_enemy - live_pokemon_player) * 5)
            + (best_effectivity * 2)
        )

    def generate_possible_attacks(
        self, combat: "Combat", is_ia: bool
    ) -> list[tuple[str, "Combat"]]:
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

        moves: list[Callable[[], str]] = [
            current_trainer.get_current_pokemon().get_move_1_name,
            current_trainer.get_current_pokemon().get_move_2_name,
            current_trainer.get_current_pokemon().get_super_move_name,
        ]

        for move in moves:
            copy_combat = copy.deepcopy(combat)
            player, enemy = copy_combat.get_players()
            current_trainer = enemy if is_ia else player
            next_trainer = player if is_ia else enemy

            damage = copy_combat.calculate_damage(
                current_trainer=current_trainer,
                next_trainer=next_trainer,
                attack=move(),
            )
            set_attack(
                current_trainer=current_trainer,
                next_trainer=next_trainer,
                damage=damage,
                combat=copy_combat,
            )

            attacks.append((move(), copy_combat))

        return attacks

    def minmax(
        self, combat: "Combat", depth: int, alpha: float, beta: float, maximizing: bool
    ) -> tuple[str | None, float]:
        if depth == 0 or combat.get_winner():
            return None, self.evaluate_heuristic(combat=combat)

        best_move = None

        if maximizing:
            max_heuristic = float("-inf")

            for move, new_combat in self.generate_possible_attacks(
                combat=combat, is_ia=True
            ):
                _, heuristic = self.minmax(
                    combat=new_combat,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    maximizing=False,
                )

                if heuristic > max_heuristic:
                    max_heuristic = heuristic
                    best_move = move

                alpha = max(alpha, heuristic)

                if beta <= alpha:
                    break

            return best_move, max_heuristic
        else:
            min_heuristic = float("inf")

            for move, new_combat in self.generate_possible_attacks(
                combat=combat, is_ia=False
            ):
                _, heuristic = self.minmax(
                    combat=new_combat,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    maximizing=True,
                )

                if heuristic < min_heuristic:
                    min_heuristic = heuristic
                    best_move = move

                beta = min(beta, heuristic)

                if beta <= alpha:
                    break

            return best_move, min_heuristic

    def choose_attack(self, combat: "Combat") -> str:
        attack, _ = self.minmax(
            combat=combat,
            depth=2,
            alpha=float("-inf"),
            beta=float("inf"),
            maximizing=True,
        )

        if attack is None:
            raise ValueError("No valid attack found")

        return attack
