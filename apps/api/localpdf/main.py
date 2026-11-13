"""Authenticated API limited to loopback peers; desktop IPC remains unimplemented."""
import hmac
import os
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

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
    if request.url.path == "/api/v1" or request.url.path.startswith("/api/v1/"):
        token = os.environ.get("LOCALPDF_SESSION_TOKEN", "")
        supplied = request.headers.get("authorization", "")
        if len(token) < 32 or not hmac.compare_digest(supplied.encode("utf-8"), ("Bearer " + token).encode("utf-8")):
            return error_response(401, "UNAUTHORIZED", "Unauthorized", request.state.request_id)
    response = await call_next(request)
    response.headers["X-Request-ID"] = request.state.request_id
    return response

@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, exc: StarletteHTTPException):
    code = {401: "UNAUTHORIZED", 403: "FORBIDDEN", 404: "NOT_FOUND", 503: "DATABASE_UNAVAILABLE"}.get(exc.status_code, "HTTP_ERROR")
    return error_response(exc.status_code, code, str(exc.detail), request.state.request_id)

@app.get("/api/v1/health")
def health():
    database = "not_configured"
    if os.environ.get("LOCALPDF_DB_PATH"):
        try:
            with closing(open_existing_database()) as db:
                db.execute("SELECT 1 FROM workspaces LIMIT 1").fetchone()
            database = "ready"
        except (HTTPException, sqlite3.Error):
            database = "unavailable"
    return {"status":"foundation", "database":database, "model":"not_configured"}


class WorkspaceCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=1, max_length=200)

    @field_validator("name")
    @classmethod
    def valid_name(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Tên không được để trống")
        return value

def open_existing_database():
    configured = os.environ.get("LOCALPDF_DB_PATH", "")
    path = Path(configured)
    if not configured or not path.is_absolute() or not path.is_file():
        raise HTTPException(status_code=503, detail="Database unavailable")
    try:
        db = sqlite3.connect(path.as_uri() + "?mode=rw", uri=True)
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=5000")
        return db
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

@app.get("/api/v1/workspaces")
def list_workspaces():
    try:
        with closing(open_existing_database()) as db:
            rows = db.execute("SELECT id,name,created_at FROM workspaces WHERE deleted_at IS NULL ORDER BY created_at DESC,id DESC").fetchall()
            return [{"id": row[0], "name": row[1], "created_at": row[2]} for row in rows]
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

@app.post("/api/v1/workspaces", status_code=201)
def create_workspace(body: WorkspaceCreate):
    workspace_id = str(uuid.uuid4())
    try:
        with closing(open_existing_database()) as db:
            with db:
                db.execute("INSERT INTO workspaces(id,name) VALUES (?,?)", (workspace_id, body.name))
                row = db.execute("SELECT id,name,created_at FROM workspaces WHERE id=?", (workspace_id,)).fetchone()
            return {"id": row[0], "name": row[1], "created_at": row[2]}
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
