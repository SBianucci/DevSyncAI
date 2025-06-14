import pytest
from fastapi.testclient import TestClient
from main import app
from unittest.mock import MagicMock

@pytest.fixture
def client():
    """Fixture que proporciona un cliente de prueba de FastAPI."""
    return TestClient(app)

@pytest.fixture
def mock_github_service(monkeypatch):
    """Fixture que proporciona un mock del servicio de GitHub."""
    mock = MagicMock()
    monkeypatch.setattr("services.github_service.GitHubService", lambda: mock)
    return mock

@pytest.fixture
def mock_jira_service(monkeypatch):
    """Fixture que proporciona un mock del servicio de Jira."""
    mock = MagicMock()
    monkeypatch.setattr("services.jira_service.JiraService", lambda: mock)
    return mock

@pytest.fixture
def mock_ai_service(monkeypatch):
    """Fixture que proporciona un mock del servicio de IA."""
    mock = MagicMock()
    monkeypatch.setattr("services.ai_service.AIService", lambda: mock)
    return mock 