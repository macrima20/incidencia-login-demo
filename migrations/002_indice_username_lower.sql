-- INC-204: desde la v1.1.0 el login busca con LOWER(username) = LOWER(?).
-- El índice UNIQUE(username) no sirve para esa expresión, así que SQLite
-- recorría toda la tabla (SCAN users) y la consulta superaba el timeout.
-- Un índice sobre la expresión LOWER(username) permite ir directo a la fila.
--
-- No es UNIQUE a propósito: antes hay que revisar si existen cuentas que solo
-- se diferencian en mayúsculas (p. ej. "JGarcia" y "jgarcia").
CREATE INDEX IF NOT EXISTS idx_users_username_lower ON users (LOWER(username));
