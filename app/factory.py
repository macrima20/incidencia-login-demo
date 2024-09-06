"""Arma la aplicación: DBConnection -> UserRepository -> AuthService -> AuthController."""
import config

from .auth_controller import AuthController
from .auth_service import AuthService
from .db import DBConnection
from .user_repository import UserRepository


class App:
    def __init__(self, users, service, controller):
        self.users = users
        self.service = service
        self.controller = controller

    def health(self):
        return {}


def _or(value, default):
    return default if value is None else value


def build_app(db_path=None, query_timeout_s=None, io_steps_per_tick=None, io_ms_per_tick=None):
    db_path = _or(db_path, config.DB_PATH)
    query_timeout_s = _or(query_timeout_s, config.QUERY_TIMEOUT_S)
    io_steps_per_tick = _or(io_steps_per_tick, config.IO_STEPS_PER_TICK)
    io_ms_per_tick = _or(io_ms_per_tick, config.IO_MS_PER_TICK)

    def connect():
        return DBConnection(db_path, query_timeout_s, io_steps_per_tick, io_ms_per_tick)

    users = UserRepository(connect)
    service = AuthService(users)
    return App(users, service, AuthController(service))
