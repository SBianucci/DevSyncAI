import pytest
from services.jira_service import JiraService
from unittest.mock import patch, MagicMock

@pytest.fixture
def jira_service():
    """Fixture que proporciona una instancia del servicio de Jira."""
    with patch.dict("os.environ", {
        "JIRA_BASE_URL": "https://test.atlassian.net",
        "JIRA_EMAIL": "test@example.com",
        "JIRA_API_TOKEN": "test_token"
    }):
        return JiraService()

def test_get_issue_transitions(jira_service):
    """Prueba el método get_issue_transitions."""
    # Configurar el mock
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "transitions": [
            {"id": "1", "to": {"name": "In Progress"}},
            {"id": "2", "to": {"name": "In Review"}},
            {"id": "3", "to": {"name": "Completed"}}
        ]
    }
    mock_response.raise_for_status.return_value = None
    
    with patch("requests.get", return_value=mock_response) as mock_get:
        # Llamar al método
        result = jira_service.get_issue_transitions("TEST-123")
        
        # Verificar la llamada
        mock_get.assert_called_once_with(
            "https://test.atlassian.net/rest/api/3/issue/TEST-123/transitions",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            auth=("test@example.com", "test_token")
        )
        
        # Verificar el resultado
        assert result == [
            {"id": "1", "to": {"name": "In Progress"}},
            {"id": "2", "to": {"name": "In Review"}},
            {"id": "3", "to": {"name": "Completed"}}
        ]

def test_transition_issue(jira_service):
    """Prueba el método transition_issue."""
    # Configurar el mock para get_issue_transitions
    mock_transitions_response = MagicMock()
    mock_transitions_response.json.return_value = {
        "transitions": [
            {"id": "1", "to": {"name": "In Progress"}},
            {"id": "2", "to": {"name": "In Review"}},
            {"id": "3", "to": {"name": "Completed"}}
        ]
    }
    mock_transitions_response.raise_for_status.return_value = None
    
    # Configurar el mock para la transición
    mock_transition_response = MagicMock()
    mock_transition_response.raise_for_status.return_value = None
    
    with patch("requests.get", return_value=mock_transitions_response) as mock_get, \
         patch("requests.post", return_value=mock_transition_response) as mock_post:
        # Llamar al método
        jira_service.transition_issue("TEST-123", "In Review")
        
        # Verificar las llamadas
        mock_get.assert_called_once_with(
            "https://test.atlassian.net/rest/api/3/issue/TEST-123/transitions",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            auth=("test@example.com", "test_token")
        )
        
        mock_post.assert_called_once_with(
            "https://test.atlassian.net/rest/api/3/issue/TEST-123/transitions",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            auth=("test@example.com", "test_token"),
            json={"transition": {"id": "2"}}
        )

def test_transition_issue_invalid_state(jira_service):
    """Prueba el método transition_issue con un estado inválido."""
    # Configurar el mock
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "transitions": [
            {"id": "1", "to": {"name": "In Progress"}},
            {"id": "2", "to": {"name": "In Review"}},
            {"id": "3", "to": {"name": "Completed"}}
        ]
    }
    mock_response.raise_for_status.return_value = None
    
    with patch("requests.get", return_value=mock_response):
        # Verificar que se lanza la excepción
        with pytest.raises(ValueError) as exc_info:
            jira_service.transition_issue("TEST-123", "Invalid State")
        
        assert str(exc_info.value) == "No se encontró la transición 'Invalid State' para la tarea TEST-123"

def test_add_comment(jira_service):
    """Prueba el método add_comment."""
    # Configurar el mock
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    
    with patch("requests.post", return_value=mock_response) as mock_post:
        # Llamar al método
        jira_service.add_comment("TEST-123", "Test comment")
        
        # Verificar la llamada
        mock_post.assert_called_once_with(
            "https://test.atlassian.net/rest/api/3/issue/TEST-123/comment",
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            auth=("test@example.com", "test_token"),
            json={
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Test comment"
                                }
                            ]
                        }
                    ]
                }
            }
        ) 