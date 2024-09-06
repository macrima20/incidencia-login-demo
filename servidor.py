"""Inicia la plataforma de demostración.

Uso:  python servidor.py    ->  http://127.0.0.1:8000   (Ctrl+C para detener)
"""
import logging
import os
import sys

import config
from app.factory import build_app
from app.http_server import serve
from app.logging_config import setup_logging
from app.migrations import pending_migrations


def main():
    setup_logging(config.LOG_PATH)
    if not os.path.exists(config.DB_PATH):
        sys.exit("No existe la base de datos. Ejecute primero:  python seed.py")
    pending = pending_migrations(config.DB_PATH)
    if pending:
        logging.getLogger("Migrations").warning(
            "Pending migrations: %s (run: python migrate.py)", ", ".join(pending))
    serve(build_app(), config.HOST, config.PORT)


if __name__ == "__main__":
    main()
