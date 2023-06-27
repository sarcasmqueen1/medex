from abc import ABC, abstractmethod
from typing import List

import pandas as pd

from medex.dto.entity import EntityType


class PluginInterface(ABC):

    @staticmethod
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        pass

    @classmethod
    @abstractmethod
    def get_param_name(cls) -> List[str]:
        pass

    @classmethod
    @abstractmethod
    def get_entity_type(cls) -> EntityType:
        pass
