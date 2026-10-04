import logging

COLORS = {
    "DEBUG": "\033[36m",  # Голубой
    "INFO": "\033[32m",  # Зеленый
    "WARNING": "\033[33m",  # Желтый
    "ERROR": "\033[31m",  # Красный
    "CRITICAL": "\033[41m",  # Красный фон
    "RESET": "\033[0m",  # Сброс цвета
}

fmt = (
    "[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)-8s -> %(message)s"
)
datefmt = "%Y-%m-%d %H:%M:%S"

formatter_file = logging.Formatter(fmt=fmt, datefmt=datefmt)


class ColoredFormatterConsole(logging.Formatter):
    def format(self, record):
        # Добавляем цвет к уровню логирования
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
            record.msg = f"{COLORS[levelname]}{record.msg}{COLORS['RESET']}"
        return super().format(record)


formatter_console = ColoredFormatterConsole(
    fmt=fmt,
    datefmt=datefmt,
)
