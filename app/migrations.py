"""Aplica en orden los archivos migrations/NNN_*.sql que aún no se han aplicado."""
import glob
import os
import sqlite3

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "migrations")

_CREATE_TABLE = (
    "CREATE TABLE IF NOT EXISTS schema_migrations ("
    " name TEXT PRIMARY KEY,"
    " applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
)


def _all_migrations(migrations_dir):
    return sorted(glob.glob(os.path.join(migrations_dir, "*.sql")))


def _applied(conn):
    conn.execute(_CREATE_TABLE)
    return {row[0] for row in conn.execute("SELECT name FROM schema_migrations")}


def pending_migrations(db_path, migrations_dir=MIGRATIONS_DIR):
    """Nombres de las migraciones que existen en el código pero no en la BD."""
    conn = sqlite3.connect(db_path)
    try:
        applied = _applied(conn)
        return [os.path.basename(p) for p in _all_migrations(migrations_dir)
                if os.path.basename(p) not in applied]
    finally:
        conn.close()


def apply_migrations(db_path, migrations_dir=MIGRATIONS_DIR):
    """Aplica las migraciones pendientes y devuelve sus nombres."""
    conn = sqlite3.connect(db_path)
    done = []
    try:
        applied = _applied(conn)
        for path in _all_migrations(migrations_dir):
            name = os.path.basename(path)
            if name in applied:
                continue
            with open(path, encoding="utf-8") as fh:
                conn.executescript(fh.read())
            conn.execute("INSERT INTO schema_migrations (name) VALUES (?)", (name,))
            conn.commit()
            done.append(name)
        return done
    finally:
        conn.close()
