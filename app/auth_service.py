"""Reglas de negocio del inicio de sesión."""
import logging
import sqlite3

from .security import new_session_token, verify_password

log = logging.getLogger("AuthService")


class AuthService:
    def __init__(self, users):
        self._users = users  # UserRepository

    def authenticate(self, username, password):
        """Devuelve un token de sesión si las credenciales son válidas; si no, None."""
        try:
            user = self._users.find_by_username(username)
            if user is None or not user["active"]:
                return None
            if not verify_password(password, user["password_hash"]):
                return None
            return new_session_token()
        except sqlite3.Error:
            log.error("Error validating user token")
            return None
