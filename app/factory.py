"""Arma la aplicación: ConnectionPool -> UserRepository -> AuthService -> AuthController."""
import config

from .auth_controller import AuthController
from .auth_service import AuthService
from .db import ConnectionPool, DBConnection
from .user_repository import UserRepository


class App:
    def __init__(self, pool, users, service, controller):
        self.pool = pool
        self.users = users
        self.service = service
        self.controller = controller

    def health(self):
        return {"pool": {"size": self.pool.size, "available": self.pool.available()}}


def _or(value, default):
    return default if value is None else value


def build_app(db_path=None, query_timeout_s=None, io_steps_per_tick=None, io_ms_per_tick=None,
              pool_size=None, pool_acquire_timeout_s=None):
    db_path = _or(db_path, config.DB_PATH)
    query_timeout_s = _or(query_timeout_s, config.QUERY_TIMEOUT_S)
    io_steps_per_tick = _or(io_steps_per_tick, config.IO_STEPS_PER_TICK)
    io_ms_per_tick = _or(io_ms_per_tick, config.IO_MS_PER_TICK)
    pool_size = _or(pool_size, config.POOL_SIZE)
    pool_acquire_timeout_s = _or(pool_acquire_timeout_s, config.POOL_ACQUIRE_TIMEOUT_S)

    def connect():
        return DBConnection(db_path, query_timeout_s, io_steps_per_tick, io_ms_per_tick)

    pool = ConnectionPool(connect, pool_size, pool_acquire_timeout_s)
    users = UserRepository(pool)
    service = AuthService(users)
    return App(pool, users, service, AuthController(service))
