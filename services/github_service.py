"""
Servicio para interactuar con la API de GitHub.
Proporciona funcionalidades para validar webhooks, obtener información de PRs
y manejar eventos de GitHub de forma segura.
"""

import hmac
import hashlib
import json
from typing import Dict, Any, Optional, List
import requests
from utils.logger import setup_logger

logger = setup_logger("github_service")

class GitHubService:
    """
    Servicio para interactuar con la API de GitHub.
    
    Attributes:
        webhook_secret (str): Secreto para validar webhooks
        api_token (str): Token de acceso personal de GitHub
        base_url (str): URL base de la API de GitHub
    """

    def __init__(
        self,
        webhook_secret: str,
        api_token: str,
        base_url: str = "https://api.github.com"
    ):
        """
        Inicializa el servicio de GitHub.

        Args:
            webhook_secret (str): Secreto para validar webhooks
            api_token (str): Token de acceso personal de GitHub
            base_url (str): URL base de la API de GitHub
        """
        self.webhook_secret = webhook_secret
        self.api_token = api_token
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"token {api_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        logger.info("GitHubService inicializado")

    def verify_webhook_signature(
        self,
        payload_body: bytes,
        signature_header: str
    ) -> bool:
        """
        Verifica la firma del webhook de GitHub.

        Args:
            payload_body (bytes): Cuerpo del payload en bytes
            signature_header (str): Header X-Hub-Signature-256

        Returns:
            bool: True si la firma es válida, False en caso contrario
        """
        if not signature_header:
            logger.warning("No se proporcionó firma en el webhook")
            return False

        try:
            expected_signature = hmac.new(
                self.webhook_secret.encode(),
                payload_body,
                hashlib.sha256
            ).hexdigest()
            
            received_signature = signature_header.replace("sha256=", "")
            
            is_valid = hmac.compare_digest(
                expected_signature,
                received_signature
            )
            
            if not is_valid:
                logger.warning("Firma de webhook inválida")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error al verificar firma: {str(e)}")
            return False

    def get_pull_request(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> Dict[str, Any]:
        """
        Obtiene información detallada de un Pull Request.

        Args:
            owner (str): Propietario del repositorio
            repo (str): Nombre del repositorio
            pr_number (int): Número del PR

        Returns:
            Dict[str, Any]: Información del PR

        Raises:
            requests.RequestException: Si hay error en la petición
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error al obtener PR #{pr_number}: {str(e)}")
            raise

    def get_pr_files(
        self,
        owner: str,
        repo: str,
        pr_number: int
    ) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de archivos modificados en un PR.

        Args:
            owner (str): Propietario del repositorio
            repo (str): Nombre del repositorio
            pr_number (int): Número del PR

        Returns:
            List[Dict[str, Any]]: Lista de archivos modificados

        Raises:
            requests.RequestException: Si hay error en la petición
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error al obtener archivos del PR #{pr_number}: {str(e)}")
            raise

    def create_pr_comment(
        self,
        owner: str,
        repo: str,
        pr_number: int,
        comment: str
    ) -> Dict[str, Any]:
        """
        Crea un comentario en un Pull Request.

        Args:
            owner (str): Propietario del repositorio
            repo (str): Nombre del repositorio
            pr_number (int): Número del PR
            comment (str): Contenido del comentario

        Returns:
            Dict[str, Any]: Respuesta de la API

        Raises:
            requests.RequestException: Si hay error en la petición
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/issues/{pr_number}/comments"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json={"body": comment}
            )
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error al crear comentario en PR #{pr_number}: {str(e)}")
            raise

    async def get_pr_diff(self, pr_number: int) -> str:
        """Obtiene el diff de un Pull Request."""
        repo = os.getenv("GITHUB_REPO")
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json().get("diff_url")
    
    async def add_pr_comment(self, pr_number: int, comment: str) -> None:
        """Añade un comentario a un Pull Request."""
        repo = os.getenv("GITHUB_REPO")
        url = f"{self.base_url}/repos/{repo}/issues/{pr_number}/comments"
        
        data = {"body": comment}
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
    
    async def get_pr_details(self, pr_number: int) -> dict:
        """Obtiene los detalles de un Pull Request."""
        repo = os.getenv("GITHUB_REPO")
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}"
        
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        
        return response.json() 