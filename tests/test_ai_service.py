import pytest
from services.ai_service import AIService
from unittest.mock import patch, MagicMock

@pytest.fixture
def ai_service():
    """Fixture que proporciona una instancia del servicio de IA."""
    with patch.dict("os.environ", {
        "VERCEL_AI_API_KEY": "test_token"
    }):
        return AIService()

def test_generate_pr_feedback(ai_service):
    """Prueba el método generate_pr_feedback."""
    # Configurar el mock
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "text": "Test feedback"
    }
    mock_response.raise_for_status.return_value = None
    
    with patch("requests.post", return_value=mock_response) as mock_post:
        # Llamar al método
        result = ai_service.generate_pr_feedback(
            "Test description",
            "Test PR"
        )
        
        # Verificar la llamada
        mock_post.assert_called_once_with(
            "https://api.vercel.com/v1/ai/generate",
            headers={
                "Authorization": "Bearer test_token",
                "Content-Type": "application/json"
            },
            json={
                "prompt": """Analiza el siguiente Pull Request y proporciona feedback constructivo:

Título: Test PR
Descripción: Test description

Por favor, proporciona:
1. Un resumen de los cambios
2. Puntos positivos
3. Sugerencias de mejora
4. Preguntas o dudas que tengas

Formato: Usa markdown para estructurar tu respuesta."""
            }
        )
        
        # Verificar el resultado
        assert result == "Test feedback"

def test_generate_document_technical(ai_service):
    """Prueba el método generate_document para documentación técnica."""
    # Configurar el mock
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "text": "Test technical doc"
    }
    mock_response.raise_for_status.return_value = None
    
    with patch("requests.post", return_value=mock_response) as mock_post:
        # Llamar al método
        result = ai_service.generate_document(
            "Test diff",
            "technical"
        )
        
        # Verificar la llamada
        mock_post.assert_called_once_with(
            "https://api.vercel.com/v1/ai/generate",
            headers={
                "Authorization": "Bearer test_token",
                "Content-Type": "application/json"
            },
            json={
                "prompt": """Genera documentación técnica detallada basada en los siguientes cambios de código:

Test diff

La documentación debe incluir:
1. Descripción técnica de los cambios
2. Impacto en el sistema
3. Consideraciones de implementación
4. Posibles efectos secundarios

Formato: Usa markdown para estructurar la documentación."""
            }
        )
        
        # Verificar el resultado
        assert result == "Test technical doc"

def test_generate_document_non_technical(ai_service):
    """Prueba el método generate_document para documentación no técnica."""
    # Configurar el mock
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "text": "Test non-technical doc"
    }
    mock_response.raise_for_status.return_value = None
    
    with patch("requests.post", return_value=mock_response) as mock_post:
        # Llamar al método
        result = ai_service.generate_document(
            "Test diff",
            "non-technical"
        )
        
        # Verificar la llamada
        mock_post.assert_called_once_with(
            "https://api.vercel.com/v1/ai/generate",
            headers={
                "Authorization": "Bearer test_token",
                "Content-Type": "application/json"
            },
            json={
                "prompt": """Genera documentación no técnica (para stakeholders) basada en los siguientes cambios:

Test diff

La documentación debe incluir:
1. Resumen ejecutivo de los cambios
2. Beneficios para el negocio
3. Impacto en los usuarios
4. Próximos pasos o consideraciones

Formato: Usa markdown para estructurar la documentación."""
            }
        )
        
        # Verificar el resultado
        assert result == "Test non-technical doc" 