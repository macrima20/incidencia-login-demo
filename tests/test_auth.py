"""Pruebas unitarias del inicio de sesión."""
import os
import shutil
import tempfile
import unittest

from app.auth_controller import MSG_INVALID_CREDENTIALS
from app.demo_data import create_database
from app.factory import build_app


class LoginTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="auth_")
        cls.db_path = os.path.join(cls.tmp, "test.db")
        create_database(cls.db_path, n_users=2000)
        # Sin latencia simulada para que las pruebas sean rápidas.
        cls.app = build_app(db_path=cls.db_path, io_ms_per_tick=0)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def login(self, username, password):
        return self.app.controller.login({"username": username, "password": password})

    def test_login_correcto(self):
        status, body = self.login("jgarcia", "Clave*2024")
        self.assertEqual(status, 200)
        self.assertTrue(body["token"])

    def test_login_ignora_mayusculas_en_el_usuario(self):
        status, _ = self.login("JGarcia", "Clave*2024")
        self.assertEqual(status, 200)

    def test_clave_incorrecta(self):
        status, body = self.login("jgarcia", "otra-clave")
        self.assertEqual(status, 401)
        self.assertEqual(body["mensaje"], MSG_INVALID_CREDENTIALS)

    def test_usuario_inexistente(self):
        status, _ = self.login("no.existe", "Clave*2024")
        self.assertEqual(status, 401)

    def test_campos_obligatorios(self):
        status, _ = self.login("", "")
        self.assertEqual(status, 400)


if __name__ == "__main__":
    unittest.main()
