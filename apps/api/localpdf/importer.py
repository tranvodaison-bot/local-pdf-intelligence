"""Trusted local import service. Never expose arbitrary paths through HTTP."""
import hashlib
import os
import uuid
from pathlib import Path

from pypdf import PdfReader

MAX_BYTES = 100 * 1024 * 1024
MAX_PAGES = 5000

class ImportFailure(Exception):
    pass

def _hash_file(stream):
    stream.seek(0)
    digest = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()

def import_pdf(db, workspace_id, selected_path, max_bytes=MAX_BYTES):
    """Register a locally selected original without modifying it; return duplicate explicitly."""
    path = Path(selected_path)
    if not path.is_absolute() or ".." in path.parts:
        raise ImportFailure("PATH_INVALID")
    try:
        # Reject links/junctions in every existing path component, not just the filename.
        for part in (path, *path.parents):
            if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
                raise ImportFailure("PATH_LINK_REJECTED")
        if not path.is_file():
            raise ImportFailure("SOURCE_MISSING")
        with path.open("rb") as stream:
            size = os.fstat(stream.fileno()).st_size
            if size > max_bytes or size == 0:
                raise ImportFailure("PDF_SIZE_INVALID")
            if stream.read(5) != b"%PDF-":
                raise ImportFailure("PDF_HEADER_INVALID")
            before = _hash_file(stream)
            stream.seek(0)
            try:
                pdf = PdfReader(stream, strict=True)
                if pdf.is_encrypted:
                    raise ImportFailure("PDF_PASSWORD_REQUIRED")
                count = len(pdf.pages)
                if count < 1 or count > MAX_PAGES:
                    raise ImportFailure("PDF_PAGE_LIMIT")
            except ImportFailure:
                raise
            except Exception as exc:
                raise ImportFailure("PDF_INVALID") from exc
            if _hash_file(stream) != before or os.fstat(stream.fileno()).st_size != size:
                raise ImportFailure("SOURCE_CHANGED")
            # Do not combine the source path provided by a browser with this function.
            if db.in_transaction:
                raise ImportFailure("TRANSACTION_ACTIVE")
            db.execute("BEGIN IMMEDIATE")
            try:
                if not db.execute("SELECT 1 FROM workspaces WHERE id=? AND deleted_at IS NULL", (workspace_id,)).fetchone():
                    raise ImportFailure("WORKSPACE_NOT_FOUND")
                duplicate = db.execute("SELECT d.id, dv.id FROM documents d JOIN document_versions dv ON dv.document_id=d.id JOIN file_assets fa ON fa.id=dv.file_asset_id WHERE d.workspace_id=? AND d.deleted_at IS NULL AND fa.sha256=? LIMIT 1", (workspace_id, before)).fetchone()
                if duplicate:
                    db.rollback()
                    return {"status": "duplicate", "document_id": duplicate[0], "version_id": duplicate[1], "sha256": before}
                asset_id, doc_id, version_id = (str(uuid.uuid4()) for _ in range(3))
                db.execute("INSERT INTO file_assets(id,sha256,original_path,byte_size) VALUES(?,?,?,?)", (asset_id, before, str(path), size))
                db.execute("INSERT INTO documents(id,workspace_id,title) VALUES(?,?,?)", (doc_id, workspace_id, path.name))
                db.execute("INSERT INTO document_versions(id,document_id,file_asset_id,version_no,status) VALUES(?,?,?,1,'PENDING')", (version_id, doc_id, asset_id))
                db.commit()
                return {"status": "imported", "document_id": doc_id, "version_id": version_id, "sha256": before, "pages": count}
            except BaseException:
                db.rollback()
                raise
    except ImportFailure:
        raise
    except OSError as exc:
        raise ImportFailure("SOURCE_UNREADABLE") from exc
