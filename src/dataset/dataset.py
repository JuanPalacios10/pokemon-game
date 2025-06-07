import pandas as pd
import os


class Dataset:
    def __init__(self) -> None:
        ruta = os.path.join(os.path.dirname(__file__), "pokedex.csv")
        self.data = pd.read_csv(ruta)

    def get_pokemon_by_name(self, name: str) -> dict[str, int | str] | str:
        result = self.data[self.data["Nombre"] == name]
        if not result.empty:
            return result.iloc[0].to_dict()
        else:
            return f"Pokemon {name} not found."

