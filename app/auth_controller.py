"""Traduce las peticiones HTTP de login a llamadas al servicio y viceversa."""
import logging

log = logging.getLogger("AuthController")

MSG_INVALID_CREDENTIALS = "Error: credenciales no válidas. Inténtelo nuevamente."
MSG_MISSING_FIELDS = "Ingrese su usuario y su contraseña."
MSG_WELCOME = "Bienvenido/a. Sesión iniciada correctamente."


class AuthController:
    def __init__(self, service):
        self._service = service  # AuthService

    def login(self, payload):
        """Devuelve (código HTTP, cuerpo JSON)."""
        username = str(payload.get("username") or "").strip()
        password = str(payload.get("password") or "")
        if not username or not password:
            return 400, {"ok": False, "mensaje": MSG_MISSING_FIELDS}

        token = self._service.authenticate(username, password)
        if token is None:
            log.warning("Login attempt failed for user: %s", username)
            return 401, {"ok": False, "mensaje": MSG_INVALID_CREDENTIALS}

        log.info("Login successful for user: %s", username)
        return 200, {"ok": True, "mensaje": MSG_WELCOME, "token": token}
