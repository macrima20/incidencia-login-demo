# Hotfix INC-204: login lento y "credenciales no válidas" con credenciales correctas

> Texto para el pull request `hotfix/error-login-204` → `main` (título = primera línea).
> Reemplace `#N` por el número del issue en GitHub para que se cierre al hacer merge.

Closes #N · Incidencia **INC-204** · Versión **1.1.1**

## Qué se cambió

| Commit | Cambio |
| --- | --- |
| `test(INC-204)` | 5 pruebas de regresión que reproducen los tres síntomas + `herramientas/plan_consulta.py` |
| `fix(db)` índice | Migración `002_indice_username_lower.sql`: índice sobre `LOWER(username)` |
| `fix(db)` pool | `ConnectionPool.connection()` devuelve siempre la conexión (try/finally); el repositorio lo usa con `with` |
| `fix(auth)` 503 | Las fallas de base de datos lanzan `AuthUnavailableError` y responden **503** con un mensaje claro y una referencia |
| `test(seguridad)` | 5 pruebas de seguridad (logs, 503, enumeración, inyección SQL, hash) |
| `chore(release)` | Versión 1.1.1 y CHANGELOG |

## Por qué se cambió

La v1.1.0 cambió la búsqueda de usuario a `LOWER(username) = LOWER(?)`. Esa
expresión no usa el índice de `username`, así que cada login recorría toda la tabla
y superaba el timeout de 6 s (**causa raíz**). Dos defectos agravaron el problema:

- el servicio reportaba el timeout como "credenciales no válidas";
- cada timeout dejaba una conexión ocupada; con 3 fallos el pool quedaba vacío y aparecía el error 500.

Detalle en `docs/INC-204/analisis_tecnico.md`.

## Evidencia de pruebas

```text
python -m unittest -v
Ran 15 tests ... OK
```

| Prueba | v1.1.0 | v1.1.1 |
| --- | --- | --- |
| Regresión INC-204 (5) | 5 fallan | 5 pasan |
| Seguridad INC-204 (5) | — | 5 pasan |
| Unitarias existentes (5) | pasan | pasan |

| Verificación manual (60 002 usuarios) | Antes (v1.1.0) | Después (v1.1.1) |
| --- | --- | --- |
| Plan de la consulta | `SCAN users` | `SEARCH users USING INDEX idx_users_username_lower` |
| Login `jgarcia` | 401 en 6,0 s | **200 en 0,02 s** |
| 4.º intento seguido | 500 | 200 |
| Conexiones libres tras 5 intentos | 0 de 3 | 3 de 3 |
| Base de datos caída | 401 "credenciales no válidas" | 503 "servicio no disponible" |

## Impacto esperado

- Los usuarios vuelven a entrar con sus credenciales en menos de 1 segundo.
- Desaparecen los errores 500 del login.
- Si la base de datos vuelve a fallar, el usuario ve un mensaje correcto y soporte recibe una referencia para buscar en los logs.
- Sin cambios en la API ni en la interfaz.

## Despliegue

1. Detener el servicio.
2. `python migrate.py` (aplica `002_indice_username_lower.sql`).
3. Iniciar el servicio y verificar `GET /api/health` → `"version": "1.1.1"`.

**Rollback:** se puede volver a v1.1.0 sin revertir la migración: el índice es compatible con esa versión.

## Checklist

- [x] Pruebas de regresión y de seguridad en verde
- [x] Sin contraseñas ni datos internos en logs o respuestas
- [x] CHANGELOG actualizado
- [x] Commits pequeños y relacionados con INC-204
