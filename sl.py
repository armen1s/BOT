from abc import abstractmethod
import pandas as pd


class SL(object):
    def __init__(self, is_dinamic: bool=False, coef: float=0.25):
        self.is_dinamic=is_dinamic
        self.coef=coef

    @abstractmethod
    def get_dinamic_sl(self, df: pd.DataFrame, position_type:int) -> float:
        pass

    def get_sl(self, df: pd.DataFrame, position_type:int) -> float:
        price=df['close']
        if not self.is_dinamic:
            return price[-1]-price[-1]*self.coef
        else: return self.get_dinamic_sl(df, position_type)




