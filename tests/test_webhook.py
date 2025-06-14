import pytest
from fastapi.testclient import TestClient
import hmac
import hashlib
import json
import os
from main import app

client = TestClient(app)

def test_health_check():
    """Prueba el endpoint de health check."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_github_webhook_invalid_signature():
    """Prueba el webhook con una firma inválida."""
    payload = {
        "ref": "refs/heads/feature/TEST-123-test-branch",
        "ref_type": "branch"
    }
    
    response = client.post(
        "/github/webhook",
        json=payload,
        headers={
            "X-GitHub-Event": "create",
            "X-Hub-Signature-256": "invalid_signature"
        }
    )
    
    assert response.status_code == 401

def test_github_webhook_branch_create():
    """Prueba la creación de una rama."""
    payload = {
        "ref": "refs/heads/feature/TEST-123-test-branch",
        "ref_type": "branch"
    }
    
    # Generar firma válida
    secret = os.getenv("GITHUB_WEBHOOK_SECRET", "test_secret")
    signature = hmac.new(
        secret.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()
    
    response = client.post(
        "/github/webhook",
        json=payload,
        headers={
            "X-GitHub-Event": "create",
            "X-Hub-Signature-256": f"sha256={signature}"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Webhook processed successfully" 