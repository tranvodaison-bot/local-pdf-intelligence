import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
from localpdf.storage import connect, migrate
from localpdf.main import app

def test_migration_idempotent_and_integrity(tmp_path):
    folder = tmp_path / "Hồ sơ tiếng Việt"
    folder.mkdir()
    db = connect(folder / "dữ liệu.sqlite")
    assert migrate(db) is True
    assert migrate(db) is False
    assert db.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO documents(id,workspace_id,title) VALUES ('d','missing','x')")
    db.close()

def test_migration_failure_rolls_back_ddl(tmp_path):
    path = tmp_path / "bad.sql"
    path.write_text("CREATE TABLE sample (id INTEGER);\nTHIS IS INVALID;\n", encoding="utf-8")
    db = connect(tmp_path / "db.sqlite")
    with pytest.raises(sqlite3.OperationalError):
        migrate(db, path)
    assert db.execute("SELECT name FROM sqlite_master WHERE name IN ('sample','migration_checksums')").fetchall() == []
    assert not db.in_transaction
    db.close()

def test_checksum_and_existing_db_rejected(tmp_path):
    migration = tmp_path / "migration.sql"
    migration.write_text("CREATE TABLE sample (id INTEGER);\n", encoding="utf-8")
    db = connect(tmp_path / "db.sqlite")
    migrate(db, migration)
    migration.write_text("CREATE TABLE sample (id TEXT);\n", encoding="utf-8")
    with pytest.raises(RuntimeError, match="checksum"):
        migrate(db, migration)
    db.close()
    other = connect(tmp_path / "old.sqlite")
    other.execute("CREATE TABLE existing (id INTEGER)")
    with pytest.raises(RuntimeError, match="adoption"):
        migrate(other, migration)
    other.close()

def test_authentication_fail_closed(monkeypatch):
    client = TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 12345))
    monkeypatch.delenv("LOCALPDF_SESSION_TOKEN", raising=False)
    assert client.get("/api/v1/health").status_code == 401
    monkeypatch.setenv("LOCALPDF_SESSION_TOKEN", "x" * 40)
    assert client.get("/api/v1/health").status_code == 401
    assert client.get("/api/v1/health", headers={"Authorization": "Bearer wrong"}).status_code == 401
    response = client.get("/api/v1/health", headers={"Authorization": "Bearer " + "x" * 40})
    assert response.status_code == 200
    assert response.json()["model"] == "not_configured"
    assert client.get("/docs").status_code == 404


def test_api_rejects_remote_and_browser_origin(monkeypatch):
    monkeypatch.setenv("LOCALPDF_SESSION_TOKEN", "x" * 40)
    headers = {"Authorization": "Bearer " + "x" * 40}
    local = TestClient(app, base_url="http://127.0.0.1", client=("127.0.0.1", 12345))
    denied = local.get("/api/v1/health", headers={**headers, "Origin":"https://example.com"})
    assert denied.status_code == 403 and denied.json()["code"] == "ORIGIN_FORBIDDEN"
    assert denied.json()["request_id"]
    remote = TestClient(app, client=("192.0.2.1", 12345))
    assert remote.get("/api/v1/health", headers=headers).json()["code"] == "LOCAL_ONLY"


def test_live_loopback_server(monkeypatch):
    import os
    import socket
    import subprocess
    import time
    import urllib.error
    import urllib.request
    api = Path(__file__).resolve().parents[1] / "apps" / "api"
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    env = dict(os.environ, LOCALPDF_SESSION_TOKEN="t" * 40, PYTHONDONTWRITEBYTECODE="1")
    process = subprocess.Popen([sys.executable, "-m", "uvicorn", "localpdf.main:app", "--host", "127.0.0.1", "--port", str(port), "--log-level", "error"], cwd=api, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        url = f"http://127.0.0.1:{port}/api/v1/health"
        for _ in range(100):
            if process.poll() is not None:
                pytest.fail("Uvicorn exited before becoming ready")
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization":"Bearer " + "t" * 40}), timeout=1) as response:
                    assert response.status == 200
                    break
            except urllib.error.URLError:
                time.sleep(0.05)
        else:
            pytest.fail("Uvicorn did not start")
        with pytest.raises(urllib.error.HTTPError) as exc:
            urllib.request.urlopen(url, timeout=1)
        assert exc.value.code == 401
    finally:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
