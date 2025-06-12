from abc import ABC
from src.pokemon.pokemon import Pokemon


class Trainer(ABC):
    """
    Clase base abstracta que representa a un entrenador de Pokémon.

    Atributos:
        __current (int): Índice del Pokémon actualmente en combate.
        __pokemon (list[Pokemon]): Lista de instancias de Pokémon del entrenador.
        __health (int): Salud actual del Pokémon activo.
        __name (str): Nombre del entrenador.
        __is_alive (bool): Indica si el entrenador aún tiene Pokémon disponibles.
    """

    def __init__(self, name: str, pokemon: list[Pokemon]):
        """
        Inicializa un entrenador con un nombre y una lista de Pokémon.

        Args:
            name (str): Nombre del entrenador.
            pokemon (list[Pokemon]): Lista de Pokémon que posee el entrenador.
        """
        self.__current = 0
        self.__pokemon = pokemon
        self.__health = pokemon[0].get_hp()
        self.__name = name
        self.__is_alive = True

    def get_name(self) -> str:
        """
        Obtiene el nombre del entrenador.

        Returns:
            str: Nombre del entrenador.
        """
        return self.__name

    def get_current_pokemon(self) -> Pokemon:
        """
        Obtiene el Pokémon actualmente en combate.

        Returns:
            Pokemon: Instancia del Pokémon activo.
        """
        return self.__pokemon[self.__current]

    def get_current_pokemon_health(self) -> int:
        """
        Obtiene la salud actual del Pokémon activo.

        Returns:
            int: Salud del Pokémon activo.
        """
        return self.__health

    def set_current_pokemon_health(self, health: int) -> None:
        """
        Establece la salud del Pokémon activo.

        Args:
            health (int): Nueva salud a asignar. Si es menor que 0, se establece en 0.
        """
        if health < 0:
            self.__health = 0
            return

        self.__health = health

    def get_live_pokemon(self) -> int:
        """
        Obtiene la cantidad de Pokémon restantes con vida.

        Returns:
            int: Número de Pokémon restantes si el entrenador está vivo, 0 en caso contrario.
        """
        if not self.is_alive():
            return 0

        return len(self.__pokemon) - self.__current

    def set_pokemon(self) -> None:
        """
        Cambia al siguiente Pokémon disponible. Si no quedan Pokémon, el entrenador queda fuera de combate.
        """
        self.__set_current_pokemon()

        if not self.is_alive():
            return None

        self.__health = self.get_current_pokemon().get_hp()

    def __set_current_pokemon(self) -> None:
        """
        Método privado para actualizar el índice del Pokémon activo.
        Si no quedan más Pokémon, marca al entrenador como fuera de combate.
        """
        if self.__current < len(self.__pokemon) - 1:
            self.__current += 1
            return

        self.__is_alive = False

    def is_current_pokemon_alive(self) -> bool:
        """
        Verifica si el Pokémon activo sigue con vida.

        Returns:
            bool: True si la salud es mayor a 0, False en caso contrario.
        """
        return self.__health > 0

    def is_alive(self) -> bool:
        """
        Verifica si el entrenador aún tiene Pokémon disponibles.

        Returns:
            bool: True si quedan Pokémon, False si está fuera de combate.
        """
        return self.__is_alive


class Player(Trainer):
    """
    Clase que representa al jugador, hereda de Trainer.
    """

    def __init__(self, pokemon: list):
        """
        Inicializa al jugador con una lista de Pokémon.

        Args:
            pokemon (list): Lista de Pokémon que posee el jugador.
        """
        super().__init__("Player", pokemon)
