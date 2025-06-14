import os
import requests
import logging
from typing import Optional, Dict, Any
from utils.logger import setup_logger
from utils.rate_limiter import rate_limiter
from fastapi import HTTPException

logger = setup_logger(__name__)

class AIServiceError(Exception):
    """Excepción base para errores del servicio de IA."""
    pass

class ContentTooLargeError(AIServiceError):
    """Excepción para cuando el contenido excede el límite permitido."""
    pass

class AIService:
    # Límites de tamaño en caracteres
    MAX_PR_DESCRIPTION_LENGTH = 4000
    MAX_PR_TITLE_LENGTH = 200
    MAX_DIFF_LENGTH = 8000
    
    def __init__(self):
        self.api_key = os.getenv("VERCEL_AI_API_KEY")
        if not self.api_key:
            raise ValueError("VERCEL_AI_API_KEY no está configurada")
            
        self.base_url = "https://api.vercel.com/v1/ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Configurar rate limiter
        self.rate_limiter = rate_limiter
    
    async def _make_ai_request(self, prompt: str) -> str:
        """Realiza una petición a la API de IA con manejo de errores y rate limiting."""
        try:
            # Verificar rate limit
            await self.rate_limiter.check_and_raise("ai_service")
            
            # Realizar petición
            response = requests.post(
                f"{self.base_url}/generate",
                headers=self.headers,
                json={"prompt": prompt},
                timeout=30  # Timeout de 30 segundos
            )
            
            # Manejar errores HTTP
            response.raise_for_status()
            
            result = response.json().get("text", "")
            if not result:
                logger.warning("La API de IA devolvió una respuesta vacía")
                return "No se pudo generar una respuesta. Por favor, intenta de nuevo."
            
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Timeout al llamar a la API de IA")
            raise HTTPException(
                status_code=504,
                detail="La API de IA no respondió a tiempo"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al llamar a la API de IA: {str(e)}")
            raise HTTPException(
                status_code=502,
                detail="Error al comunicarse con la API de IA"
            )
        except Exception as e:
            logger.error(f"Error inesperado en el servicio de IA: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Error interno del servidor"
            )
    
    async def generate_pr_feedback(self, description: str, title: str) -> str:
        """Genera feedback para un Pull Request."""
        # Validar tamaño de entrada
        if len(description) > self.MAX_PR_DESCRIPTION_LENGTH:
            logger.warning(f"Descripción de PR demasiado larga: {len(description)} caracteres")
            description = description[:self.MAX_PR_DESCRIPTION_LENGTH] + "..."
        
        if len(title) > self.MAX_PR_TITLE_LENGTH:
            logger.warning(f"Título de PR demasiado largo: {len(title)} caracteres")
            title = title[:self.MAX_PR_TITLE_LENGTH] + "..."
        
        prompt = f"""Como experto en revisión de código, analiza el siguiente Pull Request y proporciona feedback constructivo y detallado:

Título: {title}
Descripción: {description}

Por favor, proporciona un análisis estructurado que incluya:

1. Resumen de Cambios
   - Principales modificaciones realizadas
   - Alcance del cambio
   - Impacto en el sistema

2. Análisis Técnico
   - Calidad del código
   - Patrones de diseño utilizados
   - Posibles problemas de rendimiento o seguridad
   - Sugerencias de optimización

3. Buenas Prácticas
   - Aspectos positivos del código
   - Ejemplos de buenas prácticas implementadas
   - Reconocimiento de decisiones técnicas acertadas

4. Áreas de Mejora
   - Sugerencias específicas para mejorar el código
   - Alternativas o mejores prácticas recomendadas
   - Consideraciones para futuras iteraciones

5. Preguntas y Dudas
   - Puntos que requieren aclaración
   - Decisiones técnicas que podrían necesitar justificación
   - Consideraciones para el equipo

Formato: Usa markdown para estructurar tu respuesta, incluyendo:
- Encabezados para cada sección
- Listas con viñetas para puntos específicos
- Bloques de código cuando sea relevante
- Énfasis en puntos importantes usando **negrita** o *cursiva*

Nota: Sé específico y constructivo en tus comentarios, proporcionando ejemplos concretos cuando sea posible."""

        logger.info(f"Generando feedback para PR: {title}")
        return await self._make_ai_request(prompt)
    
    async def generate_document(self, content: str, doc_type: str) -> str:
        """Genera documentación técnica o no técnica."""
        # Validar tamaño de contenido
        if len(content) > self.MAX_DIFF_LENGTH:
            logger.warning(f"Diff demasiado grande: {len(content)} caracteres")
            raise ContentTooLargeError(
                f"El diff excede el límite de {self.MAX_DIFF_LENGTH} caracteres"
            )
        
        if doc_type == "technical":
            prompt = f"""Como arquitecto de software senior, genera documentación técnica detallada basada en los siguientes cambios de código:

{content}

La documentación debe incluir:

1. Descripción Técnica
   - Arquitectura y diseño implementado
   - Patrones y principios aplicados
   - Flujo de datos y control
   - Dependencias y relaciones

2. Impacto en el Sistema
   - Cambios en la arquitectura
   - Modificaciones en APIs o interfaces
   - Efectos en el rendimiento
   - Consideraciones de escalabilidad

3. Consideraciones de Implementación
   - Requisitos técnicos
   - Configuración necesaria
   - Pasos de implementación
   - Pruebas requeridas

4. Efectos Secundarios y Riesgos
   - Posibles problemas de rendimiento
   - Consideraciones de seguridad
   - Impacto en otras partes del sistema
   - Plan de mitigación de riesgos

5. Mantenimiento y Evolución
   - Recomendaciones para mantenimiento
   - Puntos de extensión
   - Consideraciones para futuras mejoras
   - Métricas y monitoreo

Formato: Usa markdown para estructurar la documentación, incluyendo:
- Diagramas en formato Mermaid cuando sea relevante
- Ejemplos de código en bloques
- Tablas para comparaciones o configuraciones
- Enlaces a documentación relacionada

Nota: La documentación debe ser clara, concisa y útil para desarrolladores técnicos."""
        else:
            prompt = f"""Como consultor de negocio y tecnología, genera documentación no técnica (para stakeholders) basada en los siguientes cambios:

{content}

La documentación debe incluir:

1. Resumen Ejecutivo
   - Objetivo principal del cambio
   - Beneficios clave
   - Impacto en el negocio
   - Timeline y entregables

2. Beneficios para el Negocio
   - Mejoras en eficiencia
   - Reducción de costos
   - Nuevas capacidades
   - Ventajas competitivas

3. Impacto en los Usuarios
   - Cambios en la experiencia de usuario
   - Nuevas funcionalidades
   - Mejoras en usabilidad
   - Plan de adopción

4. Consideraciones Estratégicas
   - Alineación con objetivos de negocio
   - Riesgos y mitigación
   - Oportunidades futuras
   - Recursos necesarios

5. Próximos Pasos
   - Plan de implementación
   - Roles y responsabilidades
   - Métricas de éxito
   - Timeline y hitos

Formato: Usa markdown para estructurar la documentación, incluyendo:
- Gráficos o diagramas cuando sea relevante
- Puntos clave resaltados
- Ejemplos prácticos
- Métricas y KPIs

Nota: La documentación debe ser clara y accesible para stakeholders no técnicos, evitando jerga técnica innecesaria."""

        logger.info(f"Generando documentación {doc_type} para cambios")
        return await self._make_ai_request(prompt) 