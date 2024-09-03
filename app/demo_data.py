"""Crea una base de datos con usuarios de prueba."""
import os
import random
import secrets
import sqlite3
import unicodedata

from .migrations import apply_migrations
from .security import hash_password

# Credenciales de PRUEBA, solo para la demo.
DEMO_USERS = [
    ("jgarcia", "Juan García", "Clave*2024"),
    ("mlopez", "María López", "Clave*2024"),
]

FIRST_NAMES = ["Ana", "Andrés", "Camila", "Carlos", "Daniela", "David", "Diana", "Felipe",
               "Juliana", "Laura", "Luis", "Manuel", "Natalia", "Paula", "Santiago",
               "Sara", "Sebastián", "Sofía", "Valentina", "Valeria"]
LAST_NAMES = ["Álvarez", "Castro", "Díaz", "Gómez", "González", "Gutiérrez", "Hernández",
              "Jiménez", "Martínez", "Moreno", "Muñoz", "Ortiz", "Pérez", "Ramírez",
              "Restrepo", "Rodríguez", "Rojas", "Sánchez", "Torres", "Vargas"]

_INSERT = "INSERT INTO users (username, full_name, email, password_hash) VALUES (?, ?, ?, ?)"


def _ascii(text):
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()


def create_database(db_path, n_users=60000, seed=204):
    """Borra y recrea la BD: n_users usuarios de relleno + los usuarios de la demo."""
    if os.path.exists(db_path):
        os.remove(db_path)
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    apply_migrations(db_path)

    rnd = random.Random(seed)
    filler_hash = hash_password(secrets.token_urlsafe(16))  # cuentas de relleno: clave aleatoria
    rows, used = [], set()
    while len(rows) < n_users:
        first, last = rnd.choice(FIRST_NAMES), rnd.choice(LAST_NAMES)
        username = "{}{}{}".format(_ascii(first)[0], _ascii(last), rnd.randint(10, 99999))
        if username in used:
            continue
        used.add(username)
        rows.append((username, "{} {}".format(first, last), username + "@universidad.edu.co", filler_hash))

    conn = sqlite3.connect(db_path)
    try:
        conn.executemany(_INSERT, rows)
        for username, full_name, password in DEMO_USERS:
            conn.execute(_INSERT, (username, full_name, username + "@universidad.edu.co",
                                   hash_password(password)))
        conn.commit()
    finally:
        conn.close()
    return n_users + len(DEMO_USERS)
