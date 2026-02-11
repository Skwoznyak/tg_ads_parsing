import logging
from datetime import datetime


def setup_logger(name='tgads_parser'):
    """
    Настройка логгера для проекта
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Создаем форматтер
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Файловый обработчик
    log_filename = f'parser_{datetime.now().strftime("%Y%m%d")}.log'
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Добавляем обработчики
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
