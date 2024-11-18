# Plataforma institucional — módulo de autenticación (demo)

Aplicación pequeña en Python que simula el inicio de sesión de la plataforma
institucional. Solo usa la biblioteca estándar (sqlite3, http.server), así que
no hay que instalar nada: basta con **Python 3.8 o superior**.

## Cómo ejecutarla

```bash
python seed.py        # crea data/app.db con 60 000 usuarios de prueba
python servidor.py    # abre http://127.0.0.1:8000
```

Usuario de prueba: `jgarcia` · contraseña `Clave*2024`.

## Pruebas

```bash
python -m unittest -v
```

## Estructura

| Carpeta / archivo   | Contenido                                             |
| ------------------- | ----------------------------------------------------- |
| `app/`              | código de la aplicación (capas controlador → servicio → repositorio → BD) |
| `migrations/`       | cambios del esquema de la base de datos, en orden     |
| `tests/`            | pruebas automáticas (`unittest`)                      |
| `config.py`         | configuración (puerto, timeouts, simulación de latencia) |
| `seed.py`           | crea la base de datos con datos de prueba             |
| `migrate.py`        | aplica las migraciones pendientes                     |
| `servidor.py`       | inicia el servidor web                                |

## Incidencia INC-204 (hotfix 1.1.1)

| Recurso | Para qué |
| --- | --- |
| `docs/INC-204/issue.md` | Descripción, evidencias y clasificación de la incidencia |
| `docs/INC-204/analisis_tecnico.md` | Reproducción, causa raíz, riesgos y seguridad |
| `docs/INC-204/pull_request.md` | Descripción del pull request |
| `tests/test_inc204_regresion.py` | Reproduce los tres síntomas (fallan en v1.1.0, pasan en v1.1.1) |
| `tests/test_inc204_seguridad.py` | Verificación mínima de seguridad |
| `herramientas/plan_consulta.py` | Muestra el plan de la consulta de login con y sin el índice |

Al pasar de la v1.1.0 a la v1.1.1 ejecute `python migrate.py` para crear el índice.

## Sobre la latencia simulada

En producción la tabla `users` es mucho más grande y está en un servidor de base
de datos remoto. Para que la demo se comporte parecido, `config.py` asigna un
costo de tiempo a cada bloque de trabajo del motor SQLite: recorrer toda la
tabla cuesta segundos y buscar por índice cuesta casi nada. Se desactiva con
`IO_MS_PER_TICK=0`.
