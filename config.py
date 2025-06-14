from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    # GitHub
    GITHUB_TOKEN: str
    GITHUB_REPO: str
    GITHUB_WEBHOOK_SECRET: str
    
    # Jira
    JIRA_BASE_URL: str
    JIRA_EMAIL: str
    JIRA_API_TOKEN: str
    
    # Vercel AI
    VERCEL_AI_API_KEY: str
    
    # Configuración de la aplicación
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración de la aplicación."""
    return Settings()

settings = get_settings() 