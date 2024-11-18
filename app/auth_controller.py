"""Traduce las peticiones HTTP de login a llamadas al servicio y viceversa."""
import logging
import uuid

from .auth_service import AuthUnavailableError

log = logging.getLogger("AuthController")

MSG_INVALID_CREDENTIALS = "Error: credenciales no válidas. Inténtelo nuevamente."
MSG_MISSING_FIELDS = "Ingrese su usuario y su contraseña."
MSG_WELCOME = "Bienvenido/a. Sesión iniciada correctamente."
MSG_UNAVAILABLE = ("El servicio de inicio de sesión no está disponible en este momento. "
                   "Intente de nuevo en unos minutos.")


class AuthController:
    def __init__(self, service):
        self._service = service  # AuthService

    def login(self, payload):
        """Devuelve (código HTTP, cuerpo JSON)."""
        username = str(payload.get("username") or "").strip()
        password = str(payload.get("password") or "")
        if not username or not password:
            return 400, {"ok": False, "mensaje": MSG_MISSING_FIELDS}

        try:
            token = self._service.authenticate(username, password)
        except AuthUnavailableError:
            # Falla del sistema (INC-204): 503 con una referencia para soporte.
            ref = uuid.uuid4().hex[:8]
            log.error("Authentication unavailable (ref=%s, user=%s)", ref, username)
            return 503, {"ok": False, "mensaje": MSG_UNAVAILABLE, "referencia": ref}

        if token is None:
            log.warning("Login attempt failed for user: %s", username)
            return 401, {"ok": False, "mensaje": MSG_INVALID_CREDENTIALS}

        log.info("Login successful for user: %s", username)
        return 200, {"ok": True, "mensaje": MSG_WELCOME, "token": token}
