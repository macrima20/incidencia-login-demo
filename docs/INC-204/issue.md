# INC-204 · Error de autenticación: "credenciales no válidas" con credenciales correctas

> Texto para crear el issue en GitHub (título = primera línea).
> Etiquetas sugeridas: `bug`, `incidencia`, `prioridad: P1`, `severidad: crítica`, `mantenimiento: correctivo`.

## Descripción

Desde las **08:34 del lunes 18/11/2024** los usuarios reportan que, al iniciar
sesión en la plataforma institucional, reciben el mensaje:

> Error: credenciales no válidas. Inténtelo nuevamente.

Varios usuarios afectados aseguran que escriben bien su usuario y su contraseña.

## Evidencias

**Logs del servidor (fragmento):**

```text
2024-11-18 08:34:22 ERROR AuthService - Error validating user token
2024-11-18 08:34:22 WARN AuthController - Login attempt failed for user: jgarcia
2024-11-18 08:34:22 ERROR DBConnection - Timeout while querying table "users"
```

**Comportamiento observado:**

- El login tarda entre 6 y 8 segundos.
- Tras varios intentos fallidos aparece un error 500.
- El módulo de autenticación se actualizó hace 24 horas (v1.1.0, desplegada el 17/11/2024 a las 08:30).

## Clasificación

| Campo | Valor | Justificación |
| --- | --- | --- |
| Tipo de mantenimiento | **Correctivo** (urgente, vía hotfix) | Corrige un defecto que ya está en producción; no agrega funciones ni adapta el sistema a un cambio externo. |
| Severidad | **Crítica (S1)** | La función principal (entrar a la plataforma) no funciona y no hay alternativa para el usuario. |
| Prioridad | **P1 – inmediata** | Afecta a muchos usuarios ahora mismo, hay riesgo reputacional y el problema empeora con el uso (error 500). |

## Impacto

- **Funcionalidad:** nadie puede iniciar sesión, así que ninguna otra función de la plataforma está disponible.
- **Experiencia de usuario:** el mensaje culpa al usuario ("credenciales no válidas"), lo que lleva a cambios de contraseña innecesarios y a más llamadas a la mesa de ayuda.
- **Reputación:** fallas visibles del servicio institucional en hora pico.

## Hipótesis inicial

Los tres eventos del log ocurren en el mismo segundo. El timeout de la consulta a
`users` (DBConnection) es el primer eslabón: el mensaje "credenciales no válidas"
sería una consecuencia, no la causa. Revisar el cambio de la v1.1.0.

## Criterios de aceptación

- [ ] Un login con credenciales correctas responde en menos de 1 segundo.
- [ ] Varios intentos fallidos seguidos no producen un error 500.
- [ ] Si la base de datos falla, el usuario ve un mensaje que no lo culpa (HTTP 503).
- [ ] Pruebas de regresión automáticas para los tres síntomas.
- [ ] Sin contraseñas ni datos internos en logs o respuestas.

**Rama:** `hotfix/error-login-204`
