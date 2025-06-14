# DevSync AI

DevSync AI es una herramienta que automatiza la actualización de estados de tareas en Jira y genera documentación técnica y no técnica para Pull Requests de GitHub, todo impulsado por FastAPI y la IA de Vercel.

## Características

- Integración automática con GitHub y Jira
- Actualización automática de estados de tareas en Jira basada en eventos de GitHub
- Generación de documentación técnica y no técnica usando IA
- Feedback automático en Pull Requests
- Validación de seguridad para webhooks de GitHub
- Rate limiting para APIs externas
- Logging centralizado
- Validación de configuración con Pydantic
- Cobertura de pruebas automatizada

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
3. Crea un archivo `.env` con las siguientes variables:
   ```
   # GitHub
   GITHUB_TOKEN=your_github_token
   GITHUB_REPO=your_github_repo
   GITHUB_WEBHOOK_SECRET=your_webhook_secret

   # Jira
   JIRA_BASE_URL=https://your-domain.atlassian.net
   JIRA_EMAIL=your_email@example.com
   JIRA_API_TOKEN=your_jira_api_token

   # Vercel AI
   VERCEL_AI_API_KEY=your_vercel_ai_api_key

   # App
   APP_ENV=development
   LOG_LEVEL=INFO
   ```

## Variables de Entorno

- `GITHUB_TOKEN`: Token de acceso personal de GitHub
- `GITHUB_REPO`: Repositorio de GitHub en formato owner/repo
- `GITHUB_WEBHOOK_SECRET`: Secreto para validar webhooks de GitHub
- `JIRA_BASE_URL`: URL base de tu instancia de Jira
- `JIRA_EMAIL`: Email de tu cuenta de Jira
- `JIRA_API_TOKEN`: Token de API de Jira
- `VERCEL_AI_API_KEY`: Clave de API de Vercel AI Gateway
- `APP_ENV`: Entorno de la aplicación (development/production)
- `LOG_LEVEL`: Nivel de logging (DEBUG/INFO/WARNING/ERROR)

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

### Ejecutar localmente

```bash
uvicorn main:app --reload
```

### Herramientas de desarrollo

El proyecto incluye varias herramientas para mantener la calidad del código:

- **Black**: Formateador de código
  ```bash
  black .
  ```

- **isort**: Organizador de imports
  ```bash
  isort .
  ```

- **flake8**: Linter
  ```bash
  flake8
  ```

- **pytest**: Tests y cobertura
  ```bash
  pytest
  ```

### Pre-commit hooks

Se recomienda configurar pre-commit hooks para ejecutar las herramientas de desarrollo automáticamente antes de cada commit. Para configurarlos:

1. Instala pre-commit:
   ```bash
   pip install pre-commit
   ```

2. Instala los hooks:
   ```bash
   pre-commit install
   ```

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request


# Trigger redeploy


## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles. 