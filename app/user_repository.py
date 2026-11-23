"""Consultas sobre la tabla users."""


class UserRepository:
    # El usuario puede escribir su nombre con mayúsculas o minúsculas:
    # "JGarcia", "jgarcia" y "JGARCIA" son la misma cuenta.
    SQL_FIND_BY_USERNAME = (
        "SELECT id, username, password_hash, active FROM users "
        "WHERE LOWER(username) = LOWER(?)"
    )

    def __init__(self, pool):
        self._pool = pool  # ConnectionPool

    def find_by_username(self, username):
        with self._pool.connection() as conn:
            return conn.query_one(self.SQL_FIND_BY_USERNAME, (username,), table="users")
