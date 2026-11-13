"""Minimal authenticated local API; no filesystem access endpoints."""
import hmac
import os
from fastapi import FastAPI, Header, HTTPException

app = FastAPI(title="Local PDF Intelligence", version="0.0.1", docs_url=None, redoc_url=None, openapi_url=None)

@app.get("/api/v1/health")
def health(authorization: str = Header(default="")):
    token = os.environ.get("LOCALPDF_SESSION_TOKEN", "")
    expected = "Bearer " + token
    if len(token) < 32 or not hmac.compare_digest(authorization, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"status": "foundation", "database": "not_configured", "model": "not_configured"}
