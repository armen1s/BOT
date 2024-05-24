import pandas as pd
import logging

logger = logging.getLogger(__name__)

class SL:
    def __init__(self, is_dynamic: bool = False, coef: float = 0.25):
        """
        Инициализация объекта SL (Stop Loss).

        Args:
        is_dynamic (bool): Определяет, будет ли стоп-лосс динамическим.
        coef (float): Коэффициент для расчёта стоп-лосса от текущей цены.
        """
        if coef <= 0:
            raise ValueError("Coefficient must be greater than 0")
        self.is_dynamic = is_dynamic
        self.coef = coef

    def calculate_sl(self, df: pd.DataFrame, position_type: str) -> float:
        """
        Рассчитывает стоп-лосс на основе последней закрытой цены и заданного коэффициента.

        Args:
        df (pd.DataFrame): DataFrame, содержащий данные о ценах.
        position_type (str): Тип позиции ('buy' или 'sell').

        Returns:
        float: Рассчитанный уровень стоп-лосса.
        """
        if df.empty or position_type not in ['buy', 'sell']:
            raise ValueError("Invalid data frame or position type")
        price = df['close'].iloc[-1]
        adjustment = price * self.coef
        stop_loss = price - adjustment if position_type == 'buy' else price + adjustment
        logger.debug(f"Calculated stop loss: {stop_loss} for position type: {position_type}")
        return stop_loss
