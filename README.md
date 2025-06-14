# DevSync AI

DevSync AI es una herramienta que automatiza la actualización de estados de tareas en Jira y genera documentación técnica y no técnica para Pull Requests de GitHub, todo impulsado por FastAPI y la IA de Vercel.

## Características

- Integración automática con GitHub y Jira
- Actualización automática de estados de tareas en Jira basada en eventos de GitHub
- Generación de documentación técnica y no técnica usando IA
- Feedback automático en Pull Requests
- Validación de seguridad para webhooks de GitHub

## Requisitos

- Python 3.8+
- Cuenta de GitHub con acceso a la API
- Cuenta de Jira con acceso a la API
- Cuenta de Vercel con acceso a Vercel AI Gateway

## Configuración

1. Clona el repositorio
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Copia `.env.example` a `.env` y configura las variables de entorno:
   ```bash
   cp .env.example .env
   ```
4. Configura las variables de entorno en el archivo `.env`

## Variables de Entorno

- `GITHUB_TOKEN`: Token de acceso personal de GitHub
- `GITHUB_REPO`: Repositorio de GitHub en formato owner/repo
- `GITHUB_WEBHOOK_SECRET`: Secreto para validar webhooks de GitHub
- `JIRA_BASE_URL`: URL base de tu instancia de Jira
- `JIRA_EMAIL`: Email de tu cuenta de Jira
- `JIRA_API_TOKEN`: Token de API de Jira
- `VERCEL_AI_API_KEY`: Clave de API de Vercel AI Gateway

## Uso

1. Despliega la aplicación en Vercel
2. Configura los webhooks en tu repositorio de GitHub:
   - Eventos: `create` (para ramas) y `pull_request`
   - URL: Tu endpoint de Vercel + `/github/webhook`
   - Secreto: El mismo que configuraste en `GITHUB_WEBHOOK_SECRET`

## Flujo de Trabajo

1. Cuando se crea una rama con un ID de Jira (ej: `feature/JIRA-123-nombre`):
   - La tarea se actualiza a "In Progress"

2. Cuando se abre un Pull Request con un ID de Jira en el título:
   - La tarea se actualiza a "In Review"
   - Se genera feedback automático en el PR

3. Cuando se mergea un Pull Request:
   - La tarea se actualiza a "Completed"
   - Se genera documentación técnica y no técnica
   - Se publica la documentación como comentario en el PR

## Desarrollo

Para ejecutar localmente:

```bash
uvicorn main:app --reload
```

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles. 