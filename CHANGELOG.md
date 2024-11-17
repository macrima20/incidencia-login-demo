# Cambios

## 1.1.0 — 2024-11-17

- El usuario ya no distingue mayúsculas y minúsculas al iniciar sesión.
- Pool de conexiones a la base de datos (3 conexiones reutilizables).
- `/api/health` muestra las conexiones libres del pool.

## 1.0.0 — 2024-09-09

- Inicio de sesión con usuario y contraseña (contraseñas con PBKDF2-SHA256).
- Endpoint `POST /api/login` y página de inicio de sesión.
- Migraciones de base de datos y datos de prueba.
