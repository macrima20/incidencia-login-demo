"""Aplica las migraciones pendientes a la base de datos.  Uso: python migrate.py"""
import config
from app.migrations import apply_migrations


def main():
    applied = apply_migrations(config.DB_PATH)
    if applied:
        for name in applied:
            print("Migración aplicada: " + name)
    else:
        print("No hay migraciones pendientes.")


if __name__ == "__main__":
    main()
