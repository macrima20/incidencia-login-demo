"""Pruebas de regresión de la incidencia INC-204 (error de autenticación).

A diferencia de tests/test_auth.py, estas pruebas usan una base con volumen
parecido al de producción (20 000 usuarios) y latencia de disco simulada.
Con el código de la v1.1.0 fallan; con la corrección pasan.
"""
import os
import shutil
import sqlite3
import tempfile
import time
import unittest
from unittest import mock

from app.auth_controller import MSG_INVALID_CREDENTIALS
from app.db import DBConnection, PoolExhaustedError, QueryTimeoutError
from app.demo_data import create_database
from app.factory import build_app
from app.user_repository import UserRepository

VALID = {"username": "jgarcia", "password": "Clave*2024"}


class Inc204RegressionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="inc204_")
        cls.db_path = os.path.join(cls.tmp, "prod_like.db")
        create_database(cls.db_path, n_users=20000)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def make_app(self, pool_size=3):
        # Producción a escala: timeout de 0,5 s y 30 ms por bloque de E/S.
        return build_app(db_path=self.db_path, query_timeout_s=0.5, io_ms_per_tick=30,
                         pool_size=pool_size, pool_acquire_timeout_s=0.1)

    # Síntoma 1: el login tarda 6-8 s y termina en timeout.
    def test_busqueda_de_usuario_usa_un_indice(self):
        conn = sqlite3.connect(self.db_path)
        try:
            plan = " | ".join(row[3] for row in conn.execute(
                "EXPLAIN QUERY PLAN " + UserRepository.SQL_FIND_BY_USERNAME, ("jgarcia",)))
        finally:
            conn.close()
        self.assertNotIn("SCAN", plan, "La consulta de login recorre toda la tabla: " + plan)

    def test_login_correcto_responde_en_menos_de_un_segundo(self):
        app = self.make_app()
        start = time.monotonic()
        status, body = app.controller.login(dict(VALID))
        elapsed = time.monotonic() - start
        self.assertEqual(status, 200, body)
        self.assertLess(elapsed, 1.0)

    # Síntoma 2: tras varios intentos fallidos aparece un error 500.
    def test_una_consulta_fallida_devuelve_la_conexion_al_pool(self):
        app = self.make_app()
        with mock.patch.object(DBConnection, "query_one", side_effect=QueryTimeoutError("simulado")):
            for _ in range(app.pool.size + 2):
                try:
                    app.users.find_by_username("jgarcia")
                except QueryTimeoutError:
                    pass  # esperado: la consulta falla
                except PoolExhaustedError:
                    self.fail("Pool agotado: las conexiones no se devuelven después de un error")
        self.assertEqual(app.pool.available(), app.pool.size)

    def test_pool_agotado_responde_503_y_no_500(self):
        app = self.make_app(pool_size=1)
        busy = app.pool.acquire()  # otra petición tiene ocupada la única conexión
        try:
            status, _ = app.controller.login(dict(VALID))
        except PoolExhaustedError:
            self.fail("PoolExhaustedError llegó al servidor: el usuario ve un error 500")
        finally:
            app.pool.release(busy)
        self.assertEqual(status, 503)

    # Síntoma 3: "credenciales no válidas" aunque las credenciales son correctas.
    def test_falla_de_base_de_datos_no_se_reporta_como_credenciales_invalidas(self):
        app = self.make_app()
        with mock.patch.object(DBConnection, "query_one", side_effect=QueryTimeoutError("simulado")):
            status, body = app.controller.login(dict(VALID))
        self.assertEqual(status, 503)
        self.assertNotEqual(body["mensaje"], MSG_INVALID_CREDENTIALS)


if __name__ == "__main__":
    unittest.main()
