import os
import requests
from typing import Optional, List, Dict

class JiraService:
    def __init__(self):
        self.base_url = os.getenv("JIRA_BASE_URL")
        self.email = os.getenv("JIRA_EMAIL")
        self.api_token = os.getenv("JIRA_API_TOKEN")
        self.auth = (self.email, self.api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    async def get_issue_transitions(self, issue_id: str) -> List[Dict]:
        """Obtiene las transiciones disponibles para una tarea."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_id}/transitions"
        
        response = requests.get(url, headers=self.headers, auth=self.auth)
        response.raise_for_status()
        
        return response.json().get("transitions", [])
    
    async def transition_issue(self, issue_id: str, transition_name: str) -> None:
        """Transiciona una tarea a un nuevo estado."""
        # Primero obtenemos las transiciones disponibles
        transitions = await self.get_issue_transitions(issue_id)
        
        # Buscamos la transición que coincida con el nombre
        transition_id = None
        for transition in transitions:
            if transition["to"]["name"].lower() == transition_name.lower():
                transition_id = transition["id"]
                break
        
        if not transition_id:
            raise ValueError(f"No se encontró la transición '{transition_name}' para la tarea {issue_id}")
        
        # Ejecutamos la transición
        url = f"{self.base_url}/rest/api/3/issue/{issue_id}/transitions"
        data = {
            "transition": {
                "id": transition_id
            }
        }
        
        response = requests.post(url, headers=self.headers, auth=self.auth, json=data)
        response.raise_for_status()
    
    async def add_comment(self, issue_id: str, comment: str) -> None:
        """Añade un comentario a una tarea."""
        url = f"{self.base_url}/rest/api/3/issue/{issue_id}/comment"
        data = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "type": "text",
                                "text": comment
                            }
                        ]
                    }
                ]
            }
        }
        
        response = requests.post(url, headers=self.headers, auth=self.auth, json=data)
        response.raise_for_status() 