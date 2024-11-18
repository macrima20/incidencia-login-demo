"""Reglas de negocio del inicio de sesión."""
import logging
import sqlite3

from .db import PoolExhaustedError
from .security import new_session_token, verify_password

log = logging.getLogger("AuthService")


class AuthUnavailableError(Exception):
    """No se pudo consultar la base de datos: es una falla del sistema, no del usuario."""


class AuthService:
    def __init__(self, users):
        self._users = users  # UserRepository

    def authenticate(self, username, password):
        """Devuelve un token si las credenciales son válidas; None si no lo son.

        Lanza AuthUnavailableError si la base de datos no responde (INC-204):
        antes ese caso se reportaba como "credenciales no válidas".
        """
        try:
            user = self._users.find_by_username(username)
        except (sqlite3.Error, PoolExhaustedError) as exc:
            log.error("User lookup failed: %s", type(exc).__name__)
            raise AuthUnavailableError() from exc
        if user is None or not user["active"]:
            return None
        if not verify_password(password, user["password_hash"]):
            return None
        return new_session_token()
