import copy
from src.combat.combat import Combat
from src.trainers.trainers import Trainer


class Enemy(Trainer):
    def __init__(self, pokemon: list):
        super().__init__("Enemy", pokemon)

    def evaluate_node(self) -> int:
        pass

    def choose_attack(self, combat: Combat) -> str:
        copy_combat = copy.deepcopy(combat)
