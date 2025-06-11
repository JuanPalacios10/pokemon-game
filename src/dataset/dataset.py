import pandas as pd
import os


class Dataset:
    def __init__(self) -> None:
        ruta = os.path.join(os.path.dirname(__file__), "pokedex.csv")
        self.data = pd.read_csv(ruta)

    def get_pokemon_by_name(self, name: str) -> dict[str, int | str]:
        result = self.data[self.data["Nombre"] == name]
        if not result.empty:
            return result.iloc[0].to_dict()

        raise ValueError(f"Pokemon with name '{name}' not found in the dataset.")

    def get_all_pokemon_names(self) -> list[str]:
        return self.data["Nombre"].tolist()
