# Файл конфигурации торговли

# Параметры торговли
SYMBOL = "BTCUSD"
LEVERAGE = 10
POSITION_SIZE = 0.01
FRAME = "4h"  # Фрейм для динамического стоп-лосса
ATR_PERIOD = 14  # Период для расчета ATR
ATR_MULTIPLIER = 2  # Множитель для расчета динамического стоп-лосса

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
