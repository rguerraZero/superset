from abc import ABCMeta, abstractmethod
import pandas as pd


class ASql(metaclass=ABCMeta):
    """Abstract sql adapter for sql database"""

    @abstractmethod
    def get_df(self, query: str) -> pd.DataFrame:
        raise NotImplementedError("get_df not implemented")
