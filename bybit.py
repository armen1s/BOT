import requests
import logging

logger = logging.getLogger(__name__)

class ByBit:
    BASE_URL = "https://api.bybit.com"

    def __init__(self, api_key, api_secret):
        """
        Инициализация API ByBit.

        Args:
        api_key (str): API ключ.
        api_secret (str): Секретный API ключ.
        """
        self.api_key = api_key
        self.api_secret = api_secret

    def fetch_ohlcv(self, symbol, timeframe):
        """
        Получение исторических данных.

        Args:
        symbol (str): Торговая пара.
        timeframe (str): Таймфрейм.

        Returns:
        list: Список свечей.
        """
        endpoint = f"{self.BASE_URL}/public/linear/kline"
        params = {
            "symbol": symbol,
            "interval": timeframe,
            "limit": 200
        }
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()["result"]

    def create_limit_buy_order(self, symbol, qty, take_profit, stop_loss):
        """
        Создание лимитного ордера на покупку.

        Args:
        symbol (str): Торговая пара.
        qty (float): Количество.
        take_profit (float): Уровень тейк-профита.
        stop_loss (float): Уровень стоп-лосса.

        Returns:
        dict: Ответ API.
        """
        endpoint = f"{self.BASE_URL}/private/linear/order/create"
        data = {
            "api_key": self.api_key,
            "symbol": symbol,
            "side": "Buy",
            "order_type": "Limit",
            "qty": qty,
            "price": take_profit,  # Используем take_profit как цену ордера
            "stop_loss": stop_loss,
            "time_in_force": "GoodTillCancel",
            "reduce_only": False,
            "close_on_trigger": False
        }
        response = requests.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()

    def create_limit_sell_order(self, symbol, qty, take_profit, stop_loss):
        """
        Создание лимитного ордера на продажу.

        Args:
        symbol (str): Торговая пара.
        qty (float): Количество.
        take_profit (float): Уровень тейк-профита.
        stop_loss (float): Уровень стоп-лосса.

        Returns:
        dict: Ответ API.
        """
        endpoint = f"{self.BASE_URL}/private/linear/order/create"
        data = {
            "api_key": self.api_key,
            "symbol": symbol,
            "side": "Sell",
            "order_type": "Limit",
            "qty": qty,
            "price": take_profit,  # Используем take_profit как цену ордера
            "stop_loss": stop_loss,
            "time_in_force": "GoodTillCancel",
            "reduce_only": False,
            "close_on_trigger": False
        }
        response = requests.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()
