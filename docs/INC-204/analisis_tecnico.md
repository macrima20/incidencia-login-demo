# INC-204 · Análisis técnico

**Resultado:** la v1.1.0 introdujo una consulta de login que recorre toda la tabla
`users` (causa raíz). Dos defectos más convirtieron esa lentitud en los síntomas
que vieron los usuarios: el mensaje engañoso y el error 500.

## 1. Reproducción

1. `git checkout v1.1.0` y `python seed.py` (60 002 usuarios, latencia simulada de producción).
2. `python servidor.py` y abrir http://127.0.0.1:8000.
3. Entrar con `jgarcia` / `Clave*2024` cuatro veces seguidas.

| Intento | Resultado | Tiempo | Conexiones libres del pool |
| --- | --- | --- | --- |
| 1 | 401 "credenciales no válidas" | 6,0 s | 2 de 3 |
| 2 | 401 "credenciales no válidas" | 6,0 s | 1 de 3 |
| 3 | 401 "credenciales no válidas" | 6,0 s | 0 de 3 |
| 4 | **500** Internal Server Error | 2,0 s | 0 de 3 |

Los logs muestran las mismas tres líneas del reporte (DBConnection, AuthService,
AuthController) y, en el intento 4, `Connection pool exhausted` con la traza de
`PoolExhaustedError`.

La reproducción automática está en `tests/test_inc204_regresion.py` (5 pruebas que
fallan con la v1.1.0).

## 2. Lectura de los logs

Las tres líneas tienen el mismo segundo, así que **el orden en que aparecen no
indica la causa**. Siguiendo el código, la secuencia real es:

1. `DBConnection`: la consulta a `users` supera `QUERY_TIMEOUT_S` (6 s) y se cancela.
2. `AuthService`: atrapa el error de base de datos, escribe "Error validating user token" (mensaje equivocado: no hay ningún token) y devuelve `None`.
3. `AuthController`: interpreta `None` como clave incorrecta y responde 401 "credenciales no válidas".

## 3. Qué cambió en la v1.1.0

`git diff v1.0.0 v1.1.0 -- app/` muestra dos cambios en el módulo de autenticación:

- **feat(auth)**: la consulta pasó de `WHERE username = ?` a `WHERE LOWER(username) = LOWER(?)`.
- **refactor(db)**: se introdujo un pool de 3 conexiones; `find_by_username` devuelve la conexión solo si la consulta termina bien (se perdió el `try/finally` de la v1.0).

Plan de ejecución (`python herramientas/plan_consulta.py`):

```text
SIN idx_users_username_lower:  SCAN users                     -> 6,02 s, cancelada por timeout
CON idx_users_username_lower:  SEARCH users USING INDEX ...    -> 0,00 s
```

## 4. Causa raíz y causas contribuyentes

| Síntoma reportado | Causa | Evidencia | Corrección |
| --- | --- | --- | --- |
| El login tarda 6-8 s | **Causa raíz:** `LOWER(username)` no puede usar el índice de `username`; SQLite recorre las 60 000 filas | `SCAN users` en el plan; `Timeout while querying table "users"` | `fix(db)`: índice sobre `LOWER(username)` (migración 002) |
| "Credenciales no válidas" con credenciales correctas | **Contribuyente:** `AuthService` trata cualquier error de BD como credenciales incorrectas | `Error validating user token` seguido de `Login attempt failed` | `fix(auth)`: falla de BD → 503 con mensaje claro |
| Error 500 tras varios intentos | **Contribuyente:** la conexión no vuelve al pool cuando la consulta falla; con 3 fallos el pool queda vacío | `Connection pool exhausted (3/3)` y traza de `PoolExhaustedError` | `fix(db)`: `with pool.connection()` (try/finally) |

**¿Por qué no lo detectaron las pruebas?** `tests/test_auth.py` usa 2 000 usuarios y
ninguna latencia: con esa base, recorrer la tabla es instantáneo. El defecto solo
aparece con volumen y latencia de producción.

## 5. Riesgos de la corrección y verificación de seguridad

| Riesgo | Mitigación |
| --- | --- |
| Crear el índice bloquea la tabla mientras se construye | En SQLite tarda menos de 1 s con 60 000 filas; en un motor grande usar creación concurrente o ventana de mantenimiento. |
| Cuentas que solo difieren en mayúsculas ("JGarcia" y "jgarcia") | El índice no es UNIQUE a propósito; revisar duplicados antes de volverlo único. |
| El mensaje 503 podría revelar detalles internos | Prueba `test_la_respuesta_503_no_expone_detalles_internos`. |
| Contraseñas en logs | Prueba `test_las_contrasenas_nunca_aparecen_en_los_logs` (éxito, fallo y 503). |
| Enumeración de usuarios | Mismo 401 y mismo mensaje para usuario inexistente y clave incorrecta (prueba). |
| Inyección SQL | Consultas parametrizadas; prueba con `' OR '1'='1' --`. |

## 6. Pendientes fuera del alcance del hotfix

- El login de un usuario inexistente responde más rápido que el de una clave incorrecta (no calcula el hash): un atacante podría usar esa diferencia de tiempo para adivinar usuarios. Abrir ticket aparte.
- `LOWER()` de SQLite solo convierte letras ASCII: "JOSÉ" y "josé" no coinciden. Evaluar normalizar el usuario al guardarlo.
- Volver UNIQUE el índice de `LOWER(username)` después de revisar duplicados.
