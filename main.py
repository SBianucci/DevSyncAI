"""
API principal de DevSync AI.
Proporciona endpoints para recibir webhooks de GitHub y generar
documentación y feedback usando IA.
"""

from fastapi import FastAPI, Request, HTTPException, Header, Depends, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import hmac
import hashlib
import os
from dotenv import load_dotenv
import json
import re
from typing import Optional, Dict, Any
from datetime import datetime

# Importar servicios y utilidades
from services.github_service import GitHubService
from services.jira_service import JiraService
from services.ai_service import AIService
from utils.logger import setup_logger
from utils.rate_limiter import RateLimiter

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logger = setup_logger("main")

# Inicializar FastAPI
app = FastAPI(
    title="DevSync AI",
    description="API para sincronización entre GitHub y Jira con IA",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar servicios
github_service = GitHubService(
    webhook_secret=os.getenv("GITHUB_WEBHOOK_SECRET"),
    api_token=os.getenv("GITHUB_TOKEN")
)

jira_service = JiraService(
    base_url=os.getenv("JIRA_BASE_URL"),
    email=os.getenv("JIRA_EMAIL"),
    api_token=os.getenv("JIRA_API_TOKEN"),
    project_key=os.getenv("JIRA_PROJECT_KEY")
)

ai_service = AIService(api_key=os.getenv("VERCEL_AI_API_KEY"))

# Configurar rate limiter
rate_limiter = RateLimiter(calls=100, period=60)  # 100 requests por minuto

def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
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
            os.getenv("GITHUB_WEBHOOK_SECRET").encode(),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        is_valid = hmac.compare_digest(
            f"sha256={expected_signature}",
            signature_header
        )
        
        if not is_valid:
            logger.warning("Firma de webhook inválida")
            
        return is_valid
        
    except Exception as e:
        logger.error(f"Error al verificar firma: {str(e)}")
        return False

def extract_jira_id(text: str) -> Optional[str]:
    """
    Extrae el ID de Jira de un texto usando regex.

    Args:
        text (str): Texto del que extraer el ID

    Returns:
        Optional[str]: ID de Jira si se encuentra, None en caso contrario
    """
    pattern = r'[A-Z]+-\d+'
    match = re.search(pattern, text)
    return match.group(0) if match else None

async def rate_limit_dependency(request: Request):
    """
    Dependencia para rate limiting.
    """
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "reset_in": f"{rate_limiter.get_reset_time(client_ip):.1f}s",
                "remaining_calls": rate_limiter.get_remaining_calls(client_ip)
            }
        )

@app.post("/github/webhook", dependencies=[Depends(rate_limit_dependency)])
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
) -> JSONResponse:
    """
    Endpoint principal para recibir webhooks de GitHub.
    Maneja eventos de creación de ramas y pull requests.

    Args:
        request (Request): Request de FastAPI
        x_github_event (str): Tipo de evento de GitHub
        x_hub_signature_256 (str): Firma del webhook

    Returns:
        JSONResponse: Respuesta con el resultado del procesamiento

    Raises:
        HTTPException: Si hay error en la firma o procesamiento
    """
    # Leer el cuerpo de la petición
    payload_body = await request.body()
    
    # Verificar la firma
    if not verify_github_signature(payload_body, x_hub_signature_256):
        logger.warning("Intento de acceso con firma inválida")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Parsear el payload
    try:
        payload = json.loads(payload_body)
    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear payload: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON payload"
        )
    
    try:
        if x_github_event == "create" and payload.get("ref_type") == "branch":
            # Manejar creación de rama
            branch_name = payload.get("ref")
            jira_id = extract_jira_id(branch_name)
            
            if jira_id:
                logger.info(f"Transicionando issue {jira_id} a 'In Progress'")
                await jira_service.update_issue_status(jira_id, "In Progress")
                
        elif x_github_event == "pull_request":
            action = payload.get("action")
            pr = payload.get("pull_request", {})
            pr_title = pr.get("title", "")
            jira_id = extract_jira_id(pr_title)
            
            if not jira_id:
                logger.info("No se encontró ID de Jira en el título del PR")
                return JSONResponse(
                    content={"message": "No Jira ID found in PR title"}
                )
            
            if action == "opened":
                # Manejar PR abierto
                logger.info(f"Procesando PR abierto para issue {jira_id}")
                await jira_service.update_issue_status(jira_id, "In Review")
                
                pr_feedback = await ai_service.generate_pr_feedback(
                    pr.get("body", ""),
                    pr_title
                )
                
                await github_service.create_pr_comment(
                    pr.get("number"),
                    pr_feedback
                )
                
            elif action == "closed" and pr.get("merged"):
                # Manejar PR mergeado
                logger.info(f"Procesando PR mergeado para issue {jira_id}")
                await jira_service.update_issue_status(jira_id, "Completed")
                
                pr_diff = await github_service.get_pr_diff(pr.get("number"))
                
                # Generar documentación
                tech_doc = await ai_service.generate_document(
                    pr_diff,
                    "technical"
                )
                non_tech_doc = await ai_service.generate_document(
                    pr_diff,
                    "non-technical"
                )
                
                # Publicar documentación
                await github_service.create_pr_comment(
                    pr.get("number"),
                    f"## Documentación Técnica\n\n{tech_doc}\n\n## Documentación No Técnica\n\n{non_tech_doc}"
                )
        
        return JSONResponse(
            content={"message": "Webhook processed successfully"}
        )
        
    except Exception as e:
        logger.error(f"Error procesando webhook: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Endpoint de health check.
    Verifica el estado de los servicios.

    Returns:
        Dict[str, Any]: Estado de los servicios
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "github": "ok",
            "jira": "ok",
            "ai": "ok"
        }
    } 