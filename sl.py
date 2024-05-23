# sl.py

import pandas as pd

class SL:
    def init(self, is_dynamic: bool=False, coef: float=0.25):
        self.is_dynamic = is_dynamic
        self.coef = coef

    def get_dynamic_sl(self, df: pd.DataFrame, position_type: str) -> float:
        price = df['close'].iloc[-1]
        if position_type == 'buy':
            return price - price * self.coef
        elif position_type == 'sell':
            return price + price * self.coef

    def get_sl(self, df: pd.DataFrame, position_type: str) -> float:
        price = df['close'].iloc[-1]
        if not self.is_dynamic:
            if position_type == 'buy':
                return price - price * self.coef
            elif position_type == 'sell':
                return price + price * self.coef
        else:
            return self.get_dynamic_sl(df, position_type)
