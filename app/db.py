"""Acceso a la base de datos SQLite."""
import logging
import sqlite3
import time

log = logging.getLogger("DBConnection")


class QueryTimeoutError(sqlite3.OperationalError):
    """La consulta superó QUERY_TIMEOUT_S y fue cancelada."""


class DBConnection:
    """Conexión SQLite con tiempo máximo por consulta y latencia de E/S simulada."""

    def __init__(self, path, query_timeout_s, io_steps_per_tick=1000, io_ms_per_tick=0.0):
        self.path = path
        self.query_timeout_s = query_timeout_s
        self.io_steps_per_tick = io_steps_per_tick
        self.io_ms_per_tick = io_ms_per_tick
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

    def query_one(self, sql, params, table):
        """Ejecuta un SELECT y devuelve la primera fila (o None)."""
        deadline = time.monotonic() + self.query_timeout_s
        pause_s = self.io_ms_per_tick / 1000.0

        def on_progress():
            if pause_s:
                time.sleep(pause_s)  # costo simulado de leer páginas del disco
            return 1 if time.monotonic() > deadline else 0  # 1 = cancelar la consulta

        self._conn.set_progress_handler(on_progress, self.io_steps_per_tick)
        try:
            cursor = self._conn.execute(sql, params)
            row = cursor.fetchone()
            cursor.close()
            return row
        except sqlite3.OperationalError as exc:
            if "interrupted" in str(exc):
                log.error('Timeout while querying table "%s"', table)
                raise QueryTimeoutError(
                    'query on table "{}" cancelled after {:.1f}s'.format(table, self.query_timeout_s)
                ) from exc
            raise
        finally:
            self._conn.set_progress_handler(None, 0)

    def close(self):
        self._conn.close()
