"""
Servicio para interactuar con la API de Jira Cloud.
Proporciona funcionalidades para crear y actualizar issues, comentarios
y manejar la integración con GitHub de forma segura.
"""

import json
from typing import Dict, Any, Optional, List
import requests
from utils.logger import setup_logger

logger = setup_logger("jira_service")

class JiraService:
    """
    Servicio para interactuar con la API de Jira Cloud.
    
    Attributes:
        base_url (str): URL base de la API de Jira
        email (str): Email de la cuenta de Jira
        api_token (str): Token de API de Jira
        project_key (str): Clave del proyecto en Jira
    """

    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
        project_key: str
    ):
        """
        Inicializa el servicio de Jira.

        Args:
            base_url (str): URL base de la API de Jira
            email (str): Email de la cuenta de Jira
            api_token (str): Token de API de Jira
            project_key (str): Clave del proyecto en Jira
        """
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_token = api_token
        self.project_key = project_key
        
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        self.auth = (email, api_token)
        logger.info("JiraService inicializado")

    def create_issue(
        self,
        summary: str,
        description: str,
        issue_type: str = "Task",
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Crea un nuevo issue en Jira.

        Args:
            summary (str): Título del issue
            description (str): Descripción detallada
            issue_type (str): Tipo de issue (default: Task)
            labels (Optional[List[str]]): Lista de etiquetas

        Returns:
            Dict[str, Any]: Información del issue creado

        Raises:
            requests.RequestException: Si hay error en la petición
        """
        url = f"{self.base_url}/rest/api/3/issue"
        
        payload = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": summary,
                "description": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}]
                        }
                    ]
                },
                "issuetype": {"name": issue_type}
            }
        }
        
        if labels:
            payload["fields"]["labels"] = labels

        try:
            response = requests.post(
                url,
                headers=self.headers,
                auth=self.auth,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error al crear issue: {str(e)}")
            raise

    def add_comment(
        self,
        issue_key: str,
        comment: str
    ) -> Dict[str, Any]:
        """
        Agrega un comentario a un issue existente.

        Args:
            issue_key (str): Clave del issue (ej: PROJ-123)
            comment (str): Contenido del comentario

        Returns:
            Dict[str, Any]: Respuesta de la API

        Raises:
            requests.RequestException: Si hay error en la petición
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/comment"
        
        payload = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": comment}]
                    }
                ]
            }
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                auth=self.auth,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error al agregar comentario a {issue_key}: {str(e)}")
            raise

    def update_issue_status(
        self,
        issue_key: str,
        status_id: str
    ) -> Dict[str, Any]:
        """
        Actualiza el estado de un issue.

        Args:
            issue_key (str): Clave del issue
            status_id (str): ID del nuevo estado

        Returns:
            Dict[str, Any]: Respuesta de la API

        Raises:
            requests.RequestException: Si hay error en la petición
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}/transitions"
        
        payload = {
            "transition": {"id": status_id}
        }

        try:
            response = requests.post(
                url,
                headers=self.headers,
                auth=self.auth,
                json=payload
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error al actualizar estado de {issue_key}: {str(e)}")
            raise

    def get_issue(self, issue_key: str) -> Dict[str, Any]:
        """
        Obtiene información detallada de un issue.

        Args:
            issue_key (str): Clave del issue

        Returns:
            Dict[str, Any]: Información del issue

        Raises:
            requests.RequestException: Si hay error en la petición
        """
        url = f"{self.base_url}/rest/api/3/issue/{issue_key}"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                auth=self.auth
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error al obtener issue {issue_key}: {str(e)}")
            raise 