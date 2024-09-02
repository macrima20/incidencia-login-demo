"""Configuración de la plataforma de demostración.

Todos los valores se pueden cambiar con variables de entorno,
por ejemplo:  PORT=9000 python servidor.py
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _float(name, default):
    return float(os.environ.get(name, default))


def _int(name, default):
    return int(os.environ.get(name, default))


# --- Servidor ----------------------------------------------------------------
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = _int("PORT", 8000)
LOG_PATH = os.environ.get("LOG_PATH", os.path.join(BASE_DIR, "logs", "app.log"))

# --- Base de datos -------------------------------------------------------------
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "data", "app.db"))
QUERY_TIMEOUT_S = _float("QUERY_TIMEOUT_S", 6.0)  # tiempo máximo por consulta

# --- Simulación de la latencia de disco de producción --------------------------
# En producción la tabla `users` es mucho más grande y vive en un servidor de
# base de datos remoto. Para que esta demo (60 000 usuarios en SQLite) se
# comporte parecido, cada bloque de IO_STEPS_PER_TICK instrucciones del motor
# SQLite "cuesta" IO_MS_PER_TICK milisegundos:
#   - recorrer toda la tabla (SCAN)        -> varios segundos
#   - buscar por índice (SEARCH ... INDEX) -> casi 0 ms
# Con IO_MS_PER_TICK=0 se desactiva la simulación.
IO_STEPS_PER_TICK = _int("IO_STEPS_PER_TICK", 1000)
IO_MS_PER_TICK = _float("IO_MS_PER_TICK", 30.0)

# --- Datos de prueba -----------------------------------------------------------
N_USERS = _int("N_USERS", 60000)
