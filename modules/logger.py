import logging
from logging.handlers import RotatingFileHandler
import os

# Створюємо папку для логів, якщо немає
if not os.path.exists('logs'):
    os.makedirs('logs')

def setup_logger():
    # Основний логер
    logger = logging.getLogger("SvitloBot")
    logger.setLevel(logging.INFO)

    # Формат: [Час] [Рівень] [Модуль] Повідомлення
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(filename)s]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Запис у файл (з ротацією)
    # maxBytes=1000000 (1MB), backupCount=5 (зберігати 5 файлів)
    file_handler = RotatingFileHandler(
        'logs/bot.log', maxBytes=1_000_000, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 2. Вивід у консоль (щоб ти бачив логи, коли запускаєш вручну)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger

# Ініціалізуємо один раз
logger = setup_logger()