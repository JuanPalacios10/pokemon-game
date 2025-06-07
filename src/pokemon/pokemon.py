from src.utils.moves import moves
import math


class Pokemon:
    def __init__(self, data: dict[str, int | str]) -> None:
        self._data = data

    def get_name(self) -> str:
        return self._data["Nombre"]

    def get_type_1(self) -> str:
        return self._data["Tipo1"]

    def get_type_2(self) -> str | None:
        tipo2 = self._data.get("Tipo2")
        return tipo2 if isinstance(tipo2, int) and not math.isnan(tipo2) else None

    def get_hp(self) -> int:
        return int(self._data["HP"])

    def get_defense(self) -> int:
        return int(self._data["Defensa"])

    def get_move_1_name(self) -> str:
        return self._data["Ataque1"]

    def get_move_2_name(self) -> str:
        return self._data["Ataque2"]

    def get_super_move_name(self) -> str:
        return self._data["SuperAtaque"]

    def get_speed(self) -> int:
        return int(self._data["Velocidad"])

    def get_damage(self, move_name: str) -> int | None:
        power = moves.get(move_name, {}).get("poder")
        if power is not None:
            return int(self._data["Ataque"]) * power

        return None

    def get_move_type(self, move_name: str) -> str | None:
        return moves.get(move_name, {}).get("tipo")
