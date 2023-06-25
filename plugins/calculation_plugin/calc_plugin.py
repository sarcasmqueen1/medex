import pandas as pd

from interfaces.plugin_interface import PluginInterface
from medex.dto.entity import EntityType


class CalcPlugin(PluginInterface):

    # Hier werden exemplarisch für jeden Patienten, die durch den Join ermittelt wurden,
    # jeweils die Werte HNR05 und Delta9 addiert.

    @staticmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        print(df)
        hnr05_numbers = df['HNR05'].tolist()
        delta9_numbers = df['Delta9'].tolist()
        name_ids = df['name_id'].tolist()

        result_list = []

        for i in range(len(hnr05_numbers)):
            result_list.append(hnr05_numbers[i] + delta9_numbers[i])

        data = {
            "name_id": name_ids,
            "value": result_list
        }
        result_df = pd.DataFrame(data)
        print(result_df)

        return result_df

    @classmethod
    def get_name(cls) -> str:
        return "hnr05_plus_delta9"

    @classmethod
    def get_param_name(cls) -> tuple[list[str], list[str]]:
        cat_keys = []
        num_keys = ['HNR05', 'Delta9']
        return cat_keys, num_keys

    @classmethod
    def get_entity_type(cls) -> EntityType:
        return EntityType.NUMERICAL


def get_plugin_class():
    return CalcPlugin
