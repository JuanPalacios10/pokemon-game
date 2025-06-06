import pandas as pd
import pprint as pp


class Dataset:
    def __init__(self) -> None:
        self.data: pd.DataFrame = pd.read_csv("pokedex.csv")

    def get_pokemon_by_name(self, name: str) -> dict[str, int | str] | str:
        result: pd.DataFrame = self.data[self.data["Nombre"] == name]
        if not result.empty:
            return result.iloc[0].to_dict()
        else:
            return f"Pokemon {name} not found."


pokemon1 = Dataset()
pp.pprint(pokemon1.get_pokemon_by_name("Pikachu"))
print(pokemon1.get_strong_pokemon())
