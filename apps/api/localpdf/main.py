"""Authenticated API limited to loopback peers; desktop IPC remains unimplemented."""
import hmac
import os
import uuid
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI(title="Local PDF Intelligence", version="0.0.1", docs_url=None, redoc_url=None, openapi_url=None)

def error_response(status, code, message, request_id):
    return JSONResponse(status_code=status, content={"code":code, "message":message, "request_id":request_id})

@app.middleware("http")
async def local_boundary(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    if request.client is None or request.client.host != "127.0.0.1":
        return error_response(403, "LOCAL_ONLY", "Local access only", request.state.request_id)
    # Browser origins are disabled until a reviewed Tauri origin is configured.
    if request.headers.get("origin"):
        return error_response(403, "ORIGIN_FORBIDDEN", "Origin not permitted", request.state.request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return error_response(exc.status_code, "UNAUTHORIZED" if exc.status_code == 401 else "HTTP_ERROR", str(exc.detail), request.state.request_id)

@app.get("/api/v1/health")
def health(authorization: str = Header(default="")):
    token = os.environ.get("LOCALPDF_SESSION_TOKEN", "")
    if len(token) < 32 or not hmac.compare_digest(authorization.encode("utf-8"), ("Bearer " + token).encode("utf-8")):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"status":"foundation", "database":"not_configured", "model":"not_configured"}
