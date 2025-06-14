import os
import requests
from typing import Optional

class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
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