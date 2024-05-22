import time
import math
import ccxt
import pandas as pd
import logging

class TradingBot:
    def __init__(self):
        # Получение API ключа и секрета из конфигурации
        self.api_key = config_api.API_KEY
        self.api_secret = config_api.API_SECRET
        # Установка символа для торговли (например, BTC/USDT)
        self.symbol = config_trading.SYMBOL
        # Установка ливмента (например, 50x)
        self.leverage = config_trading.LEVERAGE
        # Установка размера позиции (например, 10 USDT)
        self.position_size = config_trading.POSITION_SIZE
        # Установка временного интервала для получения данных с рынка (например, '1h')
        self.frame = config_trading.FRAME
        # Установка периода для вычисления ATR (например, 14)
        self.atr_period = config_trading.ATR_PERIOD
        # Установка коэффициента умножения ATR (например, 3)
        self.atr_multiplier = config_trading.ATR_MULTIPLIER
        # Инициализация логгера
        self.logger = logging.getLogger(__name__)
        # Установка уровня логирования на WARNING для основного логирования
        self.logger.setLevel(logging.WARNING)
        # Подключение к API биржи
        self.exchange = ccxt.bybit({
            'apiKey': self.api_key,
            'secret': self.api_secret,
            'enableRateLimit': True,
            'rateLimit': 3000,
            'options': {'adjustForTimeDifference': True}
        })

        # Добавление консольного обработчика для логирования с уровнем INFO и форматированием
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def connect_to_api(self):
        # Загрузка доступных рынков
        self.exchange.load_markets()
        # Информационное сообщение о подключении к API биржи
        self.logger.info("Подключено к API биржи ByBit")

    def get_account_info(self):
        try:
            # Получение информации о счете
            account_info = self.exchange.fetch_balance()
            # Информационное сообщение об информации о счете
            self.logger.info("Информация о счете: {}".format(account_info))
            # Возвращение информации о счете
            return account_info
        except Exception as e:
            # Ошибочное сообщение об ошибке при получении информации о счете
            self.logger.error("Ошибка при получении информации о счете: {}".format(str(e)))
            # Возвращение None
            return None

    def get_market_data(self):
        try:
            # Получение данных с рынка
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, self.frame)
            # Информационное сообщение о данных с рынка
            self.logger.info("Данные с рынка: {}".format(ohlcv))
            # Преобразование данных в DataFrame
            return pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        except Exception as e:
            # Ошибочное сообщение об ошибке при получении данных с рынка
            self.logger.error("Ошибкапри получении данных с рынка: {}".format(str(e)))
            # Возвращение None
            return None

    def place_order(self, order_type, price, quantity):
        try:
            # Размещение заявки
            order = self.exchange.create_order(self.symbol, order_type, quantity, price)
            # Информационное сообщение о размещенной заявке
            self.logger.info("Заявка размещена: {}".format(order))
            # Возвращение заявки
            return order
        except Exception as e:
            # Ошибочное сообщение об ошибке при размещении заявки
            self.logger.error("Ошибка при размещении заявки: {}".format(str(e)))
            # Возвращение None
            return None

    def calculate_stop_loss(self, data):
        try:
            # Вычисление ATR
            atr = data['atr'].rolling(window=self.atr_period).mean()
            # Вычисление стоп-лосса
            stop_loss = data['close'] - atr * self.atr_multiplier
            # Информационное сообщение о вычисленном стоп-лоссе
            self.logger.info("Стоп-лосс вычислен: {}".format(stop_loss))
            # Возвращение стоп-лосса
            return stop_loss
        except Exception as e:
            # Ошибочное сообщение об ошибке при вычислении стоп-лосса
            self.logger.error("Ошибка при вычислении стоп-лосса: {}".format(str(e)))
            # Возвращение None
            return None

    def start_trading(self):
        # Получение информации о счете
        account_info = self.get_account_info()
        if account_info is None:
            # Ошибочное сообщение об ошибке при получении информации о счете
            self.logger.error("Ошибка при получении информации о счете")
            # Возвращение
            return

        # Получение данных с рынка
        market_data = self.get_market_data()
        if market_data is None:
            # Ошибочное сообщение об ошибке при получении данных с рынка
            self.logger.error("Ошибка при получении данных с рынка")
            # Возвращение
            return

        while True:
            # Получение текущей цены
            current_price = market_data['close'][-1]
            # Вычисление стоп-лосса
            stop_loss = self.calculate_stop_loss(market_data)
            if stop_loss is None:
                # Ошибочное сообщение об ошибке при вычислении стоп-лосса
                self.logger.error("Ошибка при вычислении стоп-лосса")
                # Продолжение цикла
                continue

            # Проверка на наличие достаточного баланса
            if account_info['free']['USDT'] >= self.position_size:
                # Размещение заявки на покупку
                order_type = 'limit'
                price = current_price - self.position_size
                quantity = self.position_size
                self.place_order(order_type, price, quantity)
            else:
                # Предупредительное сообщение об insufficient USDT balance
                self.logger.warning("Недостаточно баланса USDT")

            # Ожидание 10 секунд
            time.sleep(10)

            # Получение новых данных с рынка
            market_data = self.get_market_data()
            if market_data is None:
                # Ошибочное сообщение об ошибкепри получении новых данных с рынка
                self.logger.error("Ошибка при получении новых данных с рынка")
                # Продолжение цикла
                continue

            # Вычисление стоп-лосса
            stop_loss = self.calculate_stop_loss(market_data)
            if stop_loss is None:
                # Ошибочное сообщение об ошибке при вычислении стоп-лосса
                self.logger.error("Ошибка при вычислении стоп-лосса")
                # Продолжение цикла
                continue
