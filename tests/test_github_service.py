import pytest
from services.github_service import GitHubService
from unittest.mock import patch, MagicMock

@pytest.fixture
def github_service():
    """Fixture que proporciona una instancia del servicio de GitHub."""
    with patch.dict("os.environ", {
        "GITHUB_TOKEN": "test_token",
        "GITHUB_REPO": "test/repo"
    }):
        return GitHubService()

def test_get_pr_diff(github_service):
    """Prueba el método get_pr_diff."""
    # Configurar el mock
    mock_response = MagicMock()
    mock_response.json.return_value = {"diff_url": "https://github.com/test/repo/pull/1.diff"}
    mock_response.raise_for_status.return_value = None
    
    with patch("requests.get", return_value=mock_response) as mock_get:
        # Llamar al método
        result = github_service.get_pr_diff(1)
        
        # Verificar la llamada
        mock_get.assert_called_once_with(
            "https://api.github.com/repos/test/repo/pulls/1",
            headers={
                "Authorization": "token test_token",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        
        # Verificar el resultado
        assert result == "https://github.com/test/repo/pull/1.diff"

def test_add_pr_comment(github_service):
    """Prueba el método add_pr_comment."""
    # Configurar el mock
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    
    with patch("requests.post", return_value=mock_response) as mock_post:
        # Llamar al método
        github_service.add_pr_comment(1, "Test comment")
        
        # Verificar la llamada
        mock_post.assert_called_once_with(
            "https://api.github.com/repos/test/repo/issues/1/comments",
            headers={
                "Authorization": "token test_token",
                "Accept": "application/vnd.github.v3+json"
            },
            json={"body": "Test comment"}
        )

def test_get_pr_details(github_service):
    """Prueba el método get_pr_details."""
    # Configurar el mock
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "number": 1,
        "title": "Test PR",
        "body": "Test description"
    }
    mock_response.raise_for_status.return_value = None
    
    with patch("requests.get", return_value=mock_response) as mock_get:
        # Llamar al método
        result = github_service.get_pr_details(1)
        
        # Verificar la llamada
        mock_get.assert_called_once_with(
            "https://api.github.com/repos/test/repo/pulls/1",
            headers={
                "Authorization": "token test_token",
                "Accept": "application/vnd.github.v3+json"
            }
        )
        
        # Verificar el resultado
        assert result == {
            "number": 1,
            "title": "Test PR",
            "body": "Test description"
        } 