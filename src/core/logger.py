import logging.config
import logging.handlers
from pathlib import Path
from queue import Queue

BASE_DIR = Path(__file__).resolve().parents[2]

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(levelname)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        },
        "detailed": {
            "format": "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z"
        }
    },
    "handlers": {
        "stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": str(LOG_DIR / "my_app.log"),
            "maxBytes": 10000,
            "backupCount": 3,
            "delay": False
        },
        "queue_handler": {
            "class": "logging.handlers.QueueHandler",
            "formatter": "detailed"
        }
    },
    "loggers": {
        "root": {
            "level": "DEBUG",
            "handlers": [
                "stderr",
                "file"
            ]
        }
    }
}


class CustomRotatingFileHandler(logging.handlers.RotatingFileHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def rotate(self, source, dest):
        # Когда происходит ротация, вызываем остановку логирования
        super().rotate(source, dest)
        logging.shutdown()


def setup_logging():
    # Очередь для передачи логов
    log_queue = Queue(-1)

    # Настраиваем конфигурацию логгирования
    logging.config.dictConfig(LOGGING_CONFIG)

    # Создаем и запускаем слушателя для логов
    queue_handler = logging.handlers.QueueHandler(log_queue)
    listener = logging.handlers.QueueListener(log_queue, *logging.getLogger().handlers)
    listener.start()

    # Добавляем QueueHandler в логгер
    logging.getLogger().addHandler(queue_handler)
