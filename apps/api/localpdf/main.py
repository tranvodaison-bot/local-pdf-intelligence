"""Authenticated API limited to loopback peers; desktop IPC remains unimplemented."""
import hmac
import hashlib
import os
import sqlite3
import uuid
from contextlib import closing
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field, field_validator
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response
from .capabilities import InvalidCapability, grants
from .importer import ImportFailure, MAX_BYTES, import_pdf
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


class DocumentImport(BaseModel):
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(min_length=1, max_length=128)
    file_selection_token: str = Field(min_length=1, max_length=128)

@app.post("/api/v1/documents/import")
def import_document(body: DocumentImport):
    try:
        path = grants.consume(body.file_selection_token, body.workspace_id)
    except InvalidCapability as exc:
        raise HTTPException(status_code=403, detail="CAPABILITY_INVALID") from exc
    try:
        with closing(open_existing_database()) as db:
            return import_pdf(db, body.workspace_id, path)
    except ImportFailure as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

@app.get("/api/v1/workspaces/{workspace_id}/documents")
def list_documents(workspace_id: str):
    try:
        with closing(open_existing_database()) as db:
            rows = db.execute("""SELECT d.id,d.title,dv.id,dv.version_no,dv.status,fa.sha256,fa.byte_size
                FROM documents d JOIN document_versions dv ON dv.document_id=d.id
                JOIN file_assets fa ON fa.id=dv.file_asset_id
                WHERE d.workspace_id=? AND d.deleted_at IS NULL ORDER BY d.created_at DESC,d.id DESC,dv.version_no DESC""", (workspace_id,)).fetchall()
            return [{"document_id":r[0],"title":r[1],"version_id":r[2],"version_no":r[3],"status":r[4],"sha256":r[5],"byte_size":r[6]} for r in rows]
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc

@app.get("/api/v1/versions/{version_id}/content")
def read_registered_document(version_id: str):
    try:
        with closing(open_existing_database()) as db:
            row = db.execute("""SELECT fa.original_path,fa.sha256,fa.byte_size FROM document_versions dv
                JOIN documents d ON d.id=dv.document_id JOIN file_assets fa ON fa.id=dv.file_asset_id
                WHERE dv.id=? AND d.deleted_at IS NULL""", (version_id,)).fetchone()
    except sqlite3.Error as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    if row is None:
        raise HTTPException(status_code=404, detail="DOCUMENT_NOT_FOUND")
    path, expected_hash, size = Path(row[0]), row[1], row[2]
    if size < 1 or size > MAX_BYTES or not isinstance(expected_hash, str) or len(expected_hash) != 64 or any(c not in "0123456789abcdef" for c in expected_hash):
        raise HTTPException(status_code=409, detail="SOURCE_INVALID")
    try:
        for part in (path, *path.parents):
            if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                raise HTTPException(status_code=409, detail="SOURCE_CHANGED")
        with path.open("rb") as source:
            initial = os.fstat(source.fileno())
            data = source.read(MAX_BYTES + 1)
            final = os.fstat(source.fileno())
            current = os.stat(path, follow_symlinks=False)
            if len(data) != size or initial.st_size != size or final.st_size != size or (final.st_dev,final.st_ino) != (current.st_dev,current.st_ino) or not hmac.compare_digest(hashlib.sha256(data).hexdigest(),expected_hash):
                raise HTTPException(status_code=409, detail="SOURCE_CHANGED")
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="SOURCE_MISSING") from exc
    except OSError as exc:
        raise HTTPException(status_code=403, detail="SOURCE_UNREADABLE") from exc
    return Response(content=data, media_type="application/pdf", headers={"Cache-Control":"no-store", "X-Content-Type-Options":"nosniff"})
