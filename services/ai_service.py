"""
Servicio para interactuar con la API de Vercel AI Gateway.
Proporciona funcionalidades para generar feedback de PRs y documentación
técnica/no técnica usando IA.
"""

import os
import requests
import logging
from typing import Optional, Dict, Any, Literal
from utils.logger import setup_logger
from utils.rate_limiter import RateLimiter
from fastapi import HTTPException, status

logger = setup_logger(__name__)

class AIServiceError(Exception):
    """Excepción base para errores del servicio de IA."""
    pass

class ContentTooLargeError(AIServiceError):
    """Excepción para cuando el contenido excede el límite permitido."""
    pass

class AIService:
    """
    Servicio para interactuar con la API de Vercel AI Gateway.
    
    Attributes:
        MAX_PR_DESCRIPTION_LENGTH (int): Límite de caracteres para descripción de PR
        MAX_PR_TITLE_LENGTH (int): Límite de caracteres para título de PR
        MAX_DIFF_LENGTH (int): Límite de caracteres para diff
        api_key (str): API key de Vercel AI
        base_url (str): URL base de la API
        rate_limiter (RateLimiter): Instancia del rate limiter
    """

    # Límites de tamaño en caracteres
    MAX_PR_DESCRIPTION_LENGTH = 4000
    MAX_PR_TITLE_LENGTH = 200
    MAX_DIFF_LENGTH = 8000
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el servicio de IA.

        Args:
            api_key (Optional[str]): API key de Vercel AI. Si no se proporciona,
                                   se busca en variables de entorno.

        Raises:
            ValueError: Si no se encuentra la API key
        """
        self.api_key = api_key or os.getenv("VERCEL_AI_API_KEY")
        if not self.api_key:
            raise ValueError("VERCEL_AI_API_KEY no está configurada")
            
        self.base_url = "https://api.vercel.com/v1/ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # Configurar rate limiter
        self.rate_limiter = RateLimiter(calls=10, period=60)  # 10 llamadas por minuto
        logger.info("AIService inicializado")
    
    async def _make_ai_request(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """
        Realiza una petición a la API de IA con manejo de errores y rate limiting.

        Args:
            prompt (str): Prompt para la IA
            max_tokens (int): Máximo número de tokens en la respuesta
            temperature (float): Temperatura para la generación (0-1)

        Returns:
            str: Respuesta generada por la IA

        Raises:
            HTTPException: Si hay error en la petición
        """
        try:
            # Verificar rate limit
            if not self.rate_limiter.is_allowed("ai_service"):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded for AI service"
                )
            
            # Realizar petición
            response = requests.post(
                f"{self.base_url}/generate",
                headers=self.headers,
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                },
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
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="La API de IA no respondió a tiempo"
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al llamar a la API de IA: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Error al comunicarse con la API de IA"
            )
        except Exception as e:
            logger.error(f"Error inesperado en el servicio de IA: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error interno del servidor"
            )
    
    async def generate_pr_feedback(
        self,
        description: str,
        title: str,
        max_tokens: int = 1024
    ) -> str:
        """
        Genera feedback para un Pull Request.

        Args:
            description (str): Descripción del PR
            title (str): Título del PR
            max_tokens (int): Máximo número de tokens en la respuesta

        Returns:
            str: Feedback generado

        Raises:
            HTTPException: Si hay error en la petición
        """
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
        return await self._make_ai_request(prompt, max_tokens=max_tokens)
    
    async def generate_document(
        self,
        content: str,
        doc_type: Literal["technical", "non-technical"],
        max_tokens: int = 2048
    ) -> str:
        """
        Genera documentación técnica o no técnica.

        Args:
            content (str): Contenido a documentar
            doc_type (Literal["technical", "non-technical"]): Tipo de documentación
            max_tokens (int): Máximo número de tokens en la respuesta

        Returns:
            str: Documentación generada

        Raises:
            ContentTooLargeError: Si el contenido excede el límite
            HTTPException: Si hay error en la petición
        """
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
        return await self._make_ai_request(prompt, max_tokens=max_tokens) 