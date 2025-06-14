from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import JSONResponse
import hmac
import hashlib
import os
from dotenv import load_dotenv
import json
import re
from typing import Optional

# Importar servicios
from services.github_service import GitHubService
from services.jira_service import JiraService
from services.ai_service import AIService

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="DevSync AI")

# Inicializar servicios
github_service = GitHubService()
jira_service = JiraService()
ai_service = AIService()

def verify_github_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verifica la firma del webhook de GitHub."""
    if not signature_header:
        return False
    
    try:
        expected_signature = hmac.new(
            os.getenv("GITHUB_WEBHOOK_SECRET").encode(),
            payload_body,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature_header)
    except Exception:
        return False

def extract_jira_id(text: str) -> Optional[str]:
    """Extrae el ID de Jira de un texto usando regex."""
    pattern = r'[A-Z]+-\d+'
    match = re.search(pattern, text)
    return match.group(0) if match else None

@app.post("/github/webhook")
async def github_webhook(
    request: Request,
    x_github_event: str = Header(None),
    x_hub_signature_256: str = Header(None)
):
    """Endpoint principal para recibir webhooks de GitHub."""
    # Leer el cuerpo de la petición
    payload_body = await request.body()
    
    # Verificar la firma
    if not verify_github_signature(payload_body, x_hub_signature_256):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parsear el payload
    payload = json.loads(payload_body)
    
    try:
        if x_github_event == "create" and payload.get("ref_type") == "branch":
            # Manejar creación de rama
            branch_name = payload.get("ref")
            jira_id = extract_jira_id(branch_name)
            if jira_id:
                await jira_service.transition_issue(jira_id, "In Progress")
                
        elif x_github_event == "pull_request":
            action = payload.get("action")
            pr = payload.get("pull_request", {})
            pr_title = pr.get("title", "")
            jira_id = extract_jira_id(pr_title)
            
            if not jira_id:
                return JSONResponse(content={"message": "No Jira ID found in PR title"})
            
            if action == "opened":
                # Manejar PR abierto
                await jira_service.transition_issue(jira_id, "In Review")
                pr_feedback = await ai_service.generate_pr_feedback(
                    pr.get("body", ""),
                    pr_title
                )
                await github_service.add_pr_comment(
                    pr.get("number"),
                    pr_feedback
                )
                
            elif action == "closed" and pr.get("merged"):
                # Manejar PR mergeado
                await jira_service.transition_issue(jira_id, "Completed")
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
                await github_service.add_pr_comment(
                    pr.get("number"),
                    f"## Documentación Técnica\n\n{tech_doc}\n\n## Documentación No Técnica\n\n{non_tech_doc}"
                )
        
        return JSONResponse(content={"message": "Webhook processed successfully"})
        
    except Exception as e:
        # Log del error (implementar logging apropiado)
        print(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health")
async def health_check():
    """Endpoint de health check."""
    return {"status": "healthy"} 