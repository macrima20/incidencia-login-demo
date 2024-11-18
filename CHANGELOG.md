# Cambios

## 1.1.1 — 2024-11-18 (hotfix INC-204)

- Corregido: el login tardaba 6-8 s y respondía "credenciales no válidas" con credenciales correctas. Nueva migración `002_indice_username_lower.sql`.
- Corregido: las conexiones no volvían al pool después de un error y aparecía un error 500.
- Las fallas de la base de datos ahora responden 503 con un mensaje claro y una referencia para soporte.
- Pruebas de regresión y de seguridad para INC-204.

## 1.1.0 — 2024-11-17

- El usuario ya no distingue mayúsculas y minúsculas al iniciar sesión.
- Pool de conexiones a la base de datos (3 conexiones reutilizables).
- `/api/health` muestra las conexiones libres del pool.

## 1.0.0 — 2024-09-09

- Inicio de sesión con usuario y contraseña (contraseñas con PBKDF2-SHA256).
- Endpoint `POST /api/login` y página de inicio de sesión.
- Migraciones de base de datos y datos de prueba.
