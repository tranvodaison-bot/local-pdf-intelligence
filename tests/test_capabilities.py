import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
from localpdf.capabilities import InvalidCapability, SelectionGrants

def test_grants_are_workspace_scoped_single_use_and_expire(tmp_path):
    now = [100.0]
    grants = SelectionGrants(ttl=10, clock=lambda: now[0])
    selected = str(tmp_path / "document.pdf")
    token = grants.issue(selected, "one")
    with pytest.raises(InvalidCapability):
        grants.consume(token, "other")
    with pytest.raises(InvalidCapability):
        grants.consume(token, "one")
    token = grants.issue(selected, "one")
    assert grants.consume(token, "one") == selected
    with pytest.raises(InvalidCapability):
        grants.consume(token, "one")
    token = grants.issue(selected, "one")
    now[0] += 10
    with pytest.raises(InvalidCapability):
        grants.consume(token, "one")

def test_grant_rejects_traversal_and_relative_path(tmp_path):
    grants = SelectionGrants()
    with pytest.raises(InvalidCapability):
        grants.issue("relative.pdf", "w")
    with pytest.raises(InvalidCapability):
        grants.issue(str(tmp_path / "dir" / ".." / "file.pdf"), "w")


def test_api_import_registered_file_and_detect_change_or_missing(tmp_path, monkeypatch):
    import hashlib
    from fastapi.testclient import TestClient
    from reportlab.pdfgen import canvas
    from localpdf.capabilities import grants
    from localpdf.main import app
    from localpdf.storage import connect, migrate
    source = tmp_path / "hồ sơ.pdf"
    pdf = canvas.Canvas(str(source)); pdf.drawString(72,720,"Synthetic"); pdf.showPage(); pdf.save()
    original = source.read_bytes()
    expected = hashlib.sha256(original).hexdigest()
    database = tmp_path / "db.sqlite"
    db = connect(database); migrate(db); db.execute("INSERT INTO workspaces(id,name) VALUES ('w','Workspace')"); db.commit(); db.close()
    monkeypatch.setenv("LOCALPDF_DB_PATH", str(database))
    monkeypatch.setenv("LOCALPDF_SESSION_TOKEN", "t" * 40)
    headers = {"Authorization":"Bearer " + "t" * 40}
    client = TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 1234))
    assert client.post("/api/v1/documents/import", headers=headers, json={"workspace_id":"w", "path":str(source)}).status_code == 422
    token = grants.issue(str(source), "w")
    payload = {"workspace_id":"w", "file_selection_token":token}
    result = client.post("/api/v1/documents/import", headers=headers, json=payload)
    assert result.status_code == 200 and result.json()["sha256"] == expected
    assert client.post("/api/v1/documents/import", headers=headers, json=payload).status_code == 403
    version = result.json()["version_id"]
    docs = client.get("/api/v1/workspaces/w/documents", headers=headers).json()
    assert docs[0]["version_id"] == version and str(source) not in str(docs)
    content = client.get(f"/api/v1/versions/{version}/content", headers=headers)
    assert content.status_code == 200 and content.content == original
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected
    real_open = Path.open
    def deny_source(path, *args, **kwargs):
        if path == source:
            raise PermissionError("simulated denial")
        return real_open(path, *args, **kwargs)
    with monkeypatch.context() as patch:
        patch.setattr(Path, "open", deny_source)
        assert client.get(f"/api/v1/versions/{version}/content", headers=headers).status_code == 403
    db = connect(database)
    db.execute("UPDATE file_assets SET sha256=?", ("0" * 64,)); db.commit(); db.close()
    assert client.get(f"/api/v1/versions/{version}/content", headers=headers).status_code == 409
    db = connect(database)
    db.execute("UPDATE file_assets SET original_path=?", (str(tmp_path / "missing.pdf"),)); db.commit(); db.close()
    assert client.get(f"/api/v1/versions/{version}/content", headers=headers).status_code == 404
    assert hashlib.sha256(source.read_bytes()).hexdigest() == expected


def test_simultaneous_grant_consumption_has_one_winner(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    grants = SelectionGrants()
    token = grants.issue(str(tmp_path / "fixture.pdf"), "w")
    def consume():
        try: return grants.consume(token, "w")
        except InvalidCapability: return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: consume(), range(2)))
    assert sum(value is not None for value in results) == 1

def test_locked_database_returns_error_without_overwriting(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from localpdf.main import app
    from localpdf.storage import connect, migrate
    database = tmp_path / "locked.sqlite"
    db = connect(database); migrate(db); db.execute("INSERT INTO workspaces(id,name) VALUES ('w','Test')"); db.commit()
    db.execute("BEGIN EXCLUSIVE")
    try:
        monkeypatch.setenv("LOCALPDF_DB_PATH", str(database))
        monkeypatch.setenv("LOCALPDF_SESSION_TOKEN", "t" * 40)
        client = TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 1234))
        response = client.get("/api/v1/workspaces", headers={"Authorization":"Bearer " + "t" * 40})
        assert response.status_code == 503
    finally:
        db.rollback()
    assert db.execute("SELECT name FROM workspaces WHERE id='w'").fetchone() == ("Test",)
    db.close()
