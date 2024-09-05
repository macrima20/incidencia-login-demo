"""Consultas sobre la tabla users."""


class UserRepository:
    SQL_FIND_BY_USERNAME = (
        "SELECT id, username, password_hash, active FROM users "
        "WHERE username = ?"
    )

    def __init__(self, connect):
        self._connect = connect  # función que abre una DBConnection

    def find_by_username(self, username):
        conn = self._connect()
        try:
            return conn.query_one(self.SQL_FIND_BY_USERNAME, (username,), table="users")
        finally:
            conn.close()
