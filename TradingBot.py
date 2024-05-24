import time
import logging
import pandas as pd
from config_api import API_KEY, API_SECRET
from trading_config import SYMBOL, LEVERAGE, POSITION_SIZE, FRAME, TAKE_PROFIT_COEF, DYNAMIC_SL_INTERVAL
from bybit import ByBit
from strategy import Strategy

logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self, api_key, api_secret, symbol, leverage, position_size, frame, take_profit_coef, sl_interval):
        """
        Инициализация торгового бота.

        Args:
        api_key (str): API ключ.
        api_secret (str): Секретный API ключ.
        symbol (str): Торговая пара.
        leverage (float): Плечо.
        position_size (float): Размер позиции.
        frame (str): Таймфрейм для анализа.
        take_profit_coef (float): Коэффициент тейк-профита.
        sl_interval (int): Интервал обновления стоп-лосса в секундах.
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.symbol = symbol
        self.leverage = leverage
        self.position_size = position_size
        self.frame = frame
        self.take_profit_coef = take_profit_coef
        self.sl_interval = sl_interval
        self.exchange = ByBit(api_key, api_secret)
        self.strategy = Strategy(symbol, leverage, position_size, frame, take_profit_coef)
        self._running = False

    def start(self):
        """
        Запуск торгового бота.
        """
        self._running = True
        logger.info("Starting trading bot")

    def stop(self):
        """
        Остановка торгового бота.
        """
        self._running = False
        logger.info("Stopping trading bot")

    def fetch_data(self):
        """
        Получение данных о ценах.

        Returns:
        pd.DataFrame: Данные о ценах.
        """
        logger.info("Fetching data")
        return self.exchange.fetch_ohlcv(self.symbol, self.frame)

    def execute_trade(self, trade_type, take_profit, stop_loss):
        """
        Выполнение торговой сделки.

        Args:
        trade_type (str): Тип сделки ('buy' или 'sell').
        take_profit (float): Уровень тейк-профита.
        stop_loss (float): Уровень стоп-лосса.
        """
        logger.info(f"Executing trade: {trade_type}")
        if trade_type == 'buy':
            return self.exchange.create_limit_buy_order(self.symbol, self.position_size, take_profit, stop_loss)
        elif trade_type == 'sell':
            return self.exchange.create_limit_sell_order(self.symbol, self.position_size, take_profit, stop_loss)

    def manage_position(self):
        """
        Управление позицией. Основной цикл торгового бота.
        """
        while self._running:
            try:
                data = self.fetch_data()
                trade_type = self.strategy.get_trade_type(data)
                if trade_type:
                    take_profit = self.strategy.get_take_profit(data, trade_type)
                    stop_loss = self.strategy.get_stop_loss(data, trade_type)
                    self.execute_trade(trade_type, take_profit, stop_loss)
                time.sleep(self.sl_interval)
            except Exception as e:
                logger.error(f"Error in managing position: {e}")

    def run(self):
        """
        Запуск основного цикла торгового бота.
        """
        self.start()
        try:
            self.manage_position()
        finally:
            self.stop()

def main():
    bot = TradingBot(
        api_key=API_KEY,
        api_secret=API_SECRET,
        symbol=SYMBOL,
        leverage=LEVERAGE,
        position_size=POSITION_SIZE,
        frame=FRAME,
        take_profit_coef=TAKE_PROFIT_COEF,
        sl_interval=DYNAMIC_SL_INTERVAL
    )
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.stop()

if __name__ == "__main__":
    main()
