"""Diagnóstico INC-204: ¿cómo ejecuta SQLite la consulta de login?

Uso (desde la carpeta del proyecto):  python herramientas/plan_consulta.py [usuario]

Muestra el plan de ejecución (EXPLAIN QUERY PLAN) y el tiempo de la consulta
en la base de datos actual y, para comparar, con/sin el índice
idx_users_username_lower. La comparación se hace dentro de una transacción
que se deshace al final: la base de datos no cambia.
"""
import os
import sqlite3
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config  # noqa: E402
from app.user_repository import UserRepository  # noqa: E402

INDEX = "idx_users_username_lower"
SQL = UserRepository.SQL_FIND_BY_USERNAME


def plan(conn, username):
    rows = conn.execute("EXPLAIN QUERY PLAN " + SQL, (username,)).fetchall()
    return " | ".join(row[3] for row in rows)


def timed_lookup(conn, username):
    """Ejecuta la consulta con la misma latencia simulada y timeout que la aplicación."""
    deadline = time.monotonic() + config.QUERY_TIMEOUT_S
    pause_s = config.IO_MS_PER_TICK / 1000.0

    def on_progress():
        if pause_s:
            time.sleep(pause_s)
        return 1 if time.monotonic() > deadline else 0

    conn.set_progress_handler(on_progress, config.IO_STEPS_PER_TICK)
    start = time.monotonic()
    try:
        found = conn.execute(SQL, (username,)).fetchone() is not None
        result = "usuario encontrado" if found else "usuario no encontrado"
    except sqlite3.OperationalError:
        result = "CANCELADA por timeout (QUERY_TIMEOUT_S = {:.1f} s)".format(config.QUERY_TIMEOUT_S)
    finally:
        conn.set_progress_handler(None, 0)
    return time.monotonic() - start, result


def report(title, conn, username):
    elapsed, result = timed_lookup(conn, username)
    print("\n[{}]".format(title))
    print("  Plan:   " + plan(conn, username))
    print("  Tiempo: {:.2f} s  -> {}".format(elapsed, result))


def has_index(conn):
    return conn.execute("SELECT 1 FROM sqlite_master WHERE type = 'index' AND name = ?",
                        (INDEX,)).fetchone() is not None


def main():
    username = sys.argv[1] if len(sys.argv) > 1 else "jgarcia"
    if not os.path.exists(config.DB_PATH):
        sys.exit("No existe la base de datos. Ejecute primero:  python seed.py")
    # cached_statements=0: sin caché, el plan se recalcula tras crear o borrar el índice
    conn = sqlite3.connect(config.DB_PATH, isolation_level=None, cached_statements=0)
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    print("Consulta de login (app/user_repository.py):\n  " + SQL)
    print("Filas en users: {:,}".format(total).replace(",", "."))

    current = has_index(conn)
    report("Base de datos actual: " + ("CON" if current else "SIN") + " " + INDEX, conn, username)

    conn.execute("BEGIN")
    try:
        if current:
            conn.execute("DROP INDEX " + INDEX)
        else:
            conn.execute("CREATE INDEX {} ON users (LOWER(username))".format(INDEX))
        report("Comparación: " + ("SIN" if current else "CON") + " " + INDEX
               + " (transacción de prueba, se deshace)", conn, username)
    finally:
        conn.execute("ROLLBACK")
        conn.close()

    print("\nLectura: SCAN = recorre toda la tabla fila por fila; "
          "SEARCH ... USING INDEX = va directo a la fila buscada.")


if __name__ == "__main__":
    main()
