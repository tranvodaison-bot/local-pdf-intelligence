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
    client = TestClient(app)
    monkeypatch.delenv("LOCALPDF_SESSION_TOKEN", raising=False)
    assert client.get("/api/v1/health").status_code == 401
    monkeypatch.setenv("LOCALPDF_SESSION_TOKEN", "x" * 40)
    assert client.get("/api/v1/health").status_code == 401
    assert client.get("/api/v1/health", headers={"Authorization": "Bearer wrong"}).status_code == 401
    response = client.get("/api/v1/health", headers={"Authorization": "Bearer " + "x" * 40})
    assert response.status_code == 200
    assert response.json()["model"] == "not_configured"
    assert client.get("/docs").status_code == 404
