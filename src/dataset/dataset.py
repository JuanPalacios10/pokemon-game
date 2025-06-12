import pandas as pd
import os


class Dataset:
    """
    Clase para manejar el dataset de Pokémon a partir de un archivo CSV.

    Métodos:
        get_pokemon_by_name(name: str) -> dict[str, int | str]:
            Devuelve un diccionario con los datos del Pokémon cuyo nombre coincide con el proporcionado.
            Lanza ValueError si el Pokémon no se encuentra.

        get_all_pokemon_names() -> list[str]:
            Devuelve una lista con todos los nombres de Pokémon en el dataset.
    """

    def __init__(self) -> None:
        """
        Inicializa la clase Dataset cargando el archivo 'pokedex.csv' ubicado en el mismo directorio.
        """
        ruta = os.path.join(os.path.dirname(__file__), "pokedex.csv")
        self.data = pd.read_csv(ruta)

    def get_pokemon_by_name(self, name: str) -> dict[str, int | str]:
        """
        Busca un Pokémon por su nombre.

        Args:
            name (str): Nombre del Pokémon a buscar.

        Returns:
            dict[str, int | str]: Diccionario con los datos del Pokémon.

        Raises:
            ValueError: Si el Pokémon no se encuentra en el dataset.
        """
        result = self.data[self.data["Nombre"] == name]
        if not result.empty:
            return result.iloc[0].to_dict()

        raise ValueError(f"Pokemon with name '{name}' not found in the dataset.")

    def get_all_pokemon_names(self) -> list[str]:
        """
        Obtiene una lista con todos los nombres de Pokémon en el dataset.

        Returns:
            list[str]: Lista de nombres de Pokémon.
        """
        return self.data["Nombre"].tolist()
