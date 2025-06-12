from src.utils.moves import moves # Importamos el diccionario con los movimientos
import math

# Creamos la clase Pokemon que representa un Pokémon con sus atributos y métodos para interactuar con ellos.
# Se creó para encapsular la información especifica de un Pokémon y proporcionar métodos para acceder a sus atributos.
# Se inicializa con un diccionario que contiene los datos del Pokémon y es retornada por el dataset.

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

    def get_damage(self, move_name: str) -> int:
        power = moves.get(move_name, {}).get("poder")
        if power is not None:
            return int(self._data["Ataque"]) * power
        return 0
        """
        Calcula y devuelve la multiplicación del ataque del Pokémon por el poder del movimiento.
        que se usará en el calculo del daño en los combates.
        """

    def get_move_type(self, move_name: str) -> str:
        return moves.get(move_name, {}).get("tipo", "")        
        """
        Devuelve el tipo del movimiento especificado. Pues es necesario en el calculo de la efectividad del ataque
        en el caso de que el Pokémon rival y aliado tengan dos tipos.
        """
