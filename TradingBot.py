import asyncio
import logging
import ccxt.async_support as ccxt
from config_api import API_KEY, API_SECRET
from config_trading import SYMBOL, LEVERAGE, POSITION_SIZE, FRAME, TAKE_PROFIT_COEF, DYNAMIC_SL_INTERVAL, MAX_DRAW_DOWN

class TradingBot:
    def init(self):
        self.exchange = ccxt.bybit({
            'apiKey': API_KEY,
            'secret': API_SECRET,
            'enableRateLimit': True
        })
        self.symbol = SYMBOL
        self.leverage = LEVERAGE
        self.position_size = POSITION_SIZE
        self.frame = FRAME
        self.max_draw_down = MAX_DRAW_DOWN
        self.current_balance = None
        self.peak_balance = None
        self.logger = logging.getLogger(name)
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    async def fetch_data(self):
        retries = 3
        for i in range(retries):
            try:
                return await self.exchange.fetch_ohlcv(self.symbol, self.frame)
            except Exception as e:
                self.logger.error(f"Attempt {i+1}: Error fetching data - {e}")
                if i < retries - 1:
                    await asyncio.sleep(2 ** i)  # Exponential backoff
                else:
                    return None

    async def execute_trade(self, decision):
        if decision:
            try:
                order = await self.exchange.create_order(self.symbol, 'limit', decision['side'], decision['amount'], decision['price'])
                self.logger.info(f"Order executed: {order}")
                await self.update_balance()
            except Exception as e:
                self.logger.error(f"Failed to place order: {e}")
        else:
            self.logger.info("No trade executed due to lack of valid decision.")

    async def update_balance(self):
        balance = await self.fetch_balance()
        if balance is not None:
            self.update_peak_balance(balance)

    async def fetch_balance(self):
        try:
            return await self.exchange.fetch_balance()
        except Exception as e:
            self.logger.error(f"Error fetching balance: {e}")
            return None

    def update_peak_balance(self, balance):
        btc_balance = balance['total']['BTC']
        self.current_balance = btc_balance
        if self.peak_balance is None or btc_balance > self.peak_balance:
            self.peak_balance = btc_balance
        self.check_draw_down()

    def check_draw_down(self):
        if self.peak_balance and self.current_balance:
            draw_down = ((self.peak_balance - self.current_balance) / self.peak_balance) * 100
            if draw_down > self.max_draw_down:
                self.logger.warning(f"Maximum draw down exceeded: {draw_down}%")
                # Implement strategy to handle draw down, e.g., pause trading, notify user, etc.

    async def run(self):
        while True:
            data = await self.fetch_data()
            if data:
                decision = await self.strategy.evaluate(data)
                await self.execute_trade(decision)
            else:
                self.logger.info("Data fetch was unsuccessful. Skipping this cycle.")
            await asyncio.sleep(DYNAMIC_SL_INTERVAL)

if name == "main":
    bot = TradingBot()
    asyncio.run(bot.run())
