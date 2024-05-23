# config_trading.py

# Параметры торговли
SYMBOL = "BTC/USDT"
LEVERAGE = 1
POSITION_SIZE = 0.01
FRAME = "1h"  # Таймфрейм для анализа

# Настройки тейк-профита и стоп-лосса
TAKE_PROFIT_COEF = 0.5  # Коэффициент для тейк-профита
DYNAMIC_SL_INTERVAL = 60  # Интервал обновления динамического стоп-лосса в секундах

# Настройки логирования
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s"

# Настройки ротации логов
LOG_FILE_NAME = "trading_bot.log"
LOG_MAX_BYTES = 5 * 1024 * 1024
LOG_BACKUP_COUNT = 5

# Функция для настройки логирования
import logging.config
import logging.handlers

def setup_logging():
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': LOG_FORMAT,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'default',
                'stream': 'ext://sys.stdout'
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': LOG_FILE_NAME,
                'mode': 'a',
                'maxBytes': LOG_MAX_BYTES,
                'backupCount': LOG_BACKUP_COUNT
            }
        },
        'loggers': {
            '': {
                'level': LOG_LEVEL,
                'handlers': ['console', 'file'],
                'propagate': True
            }
        }
    })

setup_logging()
