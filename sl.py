# sl.py

import pandas as pd

class SL:
    def init(self, is_dynamic: bool = False, coef: float = 0.25):
        """
        Инициализация объекта SL (Stop Loss).

        Args:
        is_dynamic (bool): Определяет, будет ли стоп-лосс динамическим.
        coef (float): Коэффициент для расчёта стоп-лосса от текущей цены.
        """
        self.is_dynamic = is_dynamic
        self.coef = coef

    async def calculate_sl(self, df: pd.DataFrame, position_type: str) -> float:
        """
        Асинхронно рассчитывает стоп-лосс на основе последней закрытой цены и заданного коэффициента.

        Args:
        df (pd.DataFrame): DataFrame, содержащий данные о ценах.
        position_type (str): Тип позиции ('buy' или 'sell').

        Returns:
        float: Рассчитанный уровень стоп-лосса.
        """
        price = df['close'].iloc[-1]
        adjustment = price * self.coef
        if position_type == 'buy':
            return price - adjustment
        elif position_type == 'sell':
            return price + adjustment
        else:
            raise ValueError("Invalid position type provided. Use 'buy' or 'sell'.")
