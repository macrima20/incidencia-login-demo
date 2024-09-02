"""Formato de logs: 2024-11-18 08:34:22 ERROR AuthService - mensaje"""
import logging
import os

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(log_path=None, level=logging.INFO):
    """Envía los logs a la consola y, si se indica, a un archivo."""
    logging.addLevelName(logging.WARNING, "WARN")
    root = logging.getLogger()
    if getattr(root, "_platform_configured", False):
        return
    formatter = logging.Formatter(LOG_FORMAT, DATE_FORMAT)
    handlers = [logging.StreamHandler()]
    if log_path:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))
    for handler in handlers:
        handler.setFormatter(formatter)
        root.addHandler(handler)
    root.setLevel(level)
    root._platform_configured = True
