import os
import requests
from typing import Optional

class AIService:
    def __init__(self):
        self.api_key = os.getenv("VERCEL_AI_API_KEY")
        self.base_url = "https://api.vercel.com/v1/ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_pr_feedback(self, description: str, title: str) -> str:
        """Genera feedback para un Pull Request."""
        prompt = f"""Analiza el siguiente Pull Request y proporciona feedback constructivo:

Título: {title}
Descripción: {description}

Por favor, proporciona:
1. Un resumen de los cambios
2. Puntos positivos
3. Sugerencias de mejora
4. Preguntas o dudas que tengas

Formato: Usa markdown para estructurar tu respuesta."""

        response = requests.post(
            f"{self.base_url}/generate",
            headers=self.headers,
            json={"prompt": prompt}
        )
        response.raise_for_status()
        
        return response.json().get("text", "")
    
    async def generate_document(self, content: str, doc_type: str) -> str:
        """Genera documentación técnica o no técnica."""
        if doc_type == "technical":
            prompt = f"""Genera documentación técnica detallada basada en los siguientes cambios de código:

{content}

La documentación debe incluir:
1. Descripción técnica de los cambios
2. Impacto en el sistema
3. Consideraciones de implementación
4. Posibles efectos secundarios

Formato: Usa markdown para estructurar la documentación."""
        else:
            prompt = f"""Genera documentación no técnica (para stakeholders) basada en los siguientes cambios:

{content}

La documentación debe incluir:
1. Resumen ejecutivo de los cambios
2. Beneficios para el negocio
3. Impacto en los usuarios
4. Próximos pasos o consideraciones

Formato: Usa markdown para estructurar la documentación."""

        response = requests.post(
            f"{self.base_url}/generate",
            headers=self.headers,
            json={"prompt": prompt}
        )
        response.raise_for_status()
        
        return response.json().get("text", "") 