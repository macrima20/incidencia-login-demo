"""Verificación mínima de seguridad de la corrección INC-204.

Revisa que el cambio no exponga credenciales, datos sensibles ni detalles
internos, y que el login siga sin revelar si un usuario existe.
"""
import json
import os
import shutil
import sqlite3
import tempfile
import unittest
from unittest import mock

from app.db import DBConnection, QueryTimeoutError
from app.demo_data import create_database
from app.factory import build_app

PASSWORD = "Clave*2024"
WRONG_PASSWORD = "Secreta-Incorrecta-123"


class Inc204SecurityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="inc204_sec_")
        cls.db_path = os.path.join(cls.tmp, "test.db")
        create_database(cls.db_path, n_users=2000)
        cls.app = build_app(db_path=cls.db_path, io_ms_per_tick=0)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def login(self, username, password):
        return self.app.controller.login({"username": username, "password": password})

    def test_las_contrasenas_nunca_aparecen_en_los_logs(self):
        with self.assertLogs(level="DEBUG") as captured:
            self.login("jgarcia", PASSWORD)
            self.login("jgarcia", WRONG_PASSWORD)
            with mock.patch.object(DBConnection, "query_one", side_effect=QueryTimeoutError("simulado")):
                self.login("jgarcia", PASSWORD)
        logs = "\n".join(captured.output)
        self.assertNotIn(PASSWORD, logs)
        self.assertNotIn(WRONG_PASSWORD, logs)

    def test_la_respuesta_503_no_expone_detalles_internos(self):
        error = QueryTimeoutError('query on table "users" cancelled after 6.0s')
        with mock.patch.object(DBConnection, "query_one", side_effect=error):
            status, body = self.login("jgarcia", PASSWORD)
        self.assertEqual(status, 503)
        text = json.dumps(body, ensure_ascii=False).lower()
        for internal in ("sqlite", "select", "users", "timeout", "traceback", "error"):
            self.assertNotIn(internal, text)

    def test_mismo_mensaje_para_usuario_inexistente_y_clave_incorrecta(self):
        # No revelar si una cuenta existe (enumeración de usuarios).
        self.assertEqual(self.login("no.existe", WRONG_PASSWORD), self.login("jgarcia", WRONG_PASSWORD))

    def test_inyeccion_sql_en_el_usuario_no_da_acceso(self):
        status, _ = self.login("' OR '1'='1' --", WRONG_PASSWORD)
        self.assertEqual(status, 401)

    def test_las_contrasenas_se_guardan_con_hash(self):
        conn = sqlite3.connect(self.db_path)
        try:
            stored = conn.execute("SELECT password_hash FROM users WHERE username = 'jgarcia'").fetchone()[0]
        finally:
            conn.close()
        self.assertTrue(stored.startswith("pbkdf2_sha256$"))
        self.assertNotIn(PASSWORD, stored)


if __name__ == "__main__":
    unittest.main()
