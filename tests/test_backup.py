import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
from localpdf.backup import BackupError, copy_database
from localpdf.storage import connect, migrate

def test_backup_restore_preserves_database_and_refuses_overwrite(tmp_path):
    source = tmp_path / "nguồn.sqlite"
    db = connect(source)
    migrate(db)
    db.execute("INSERT INTO workspaces(id,name) VALUES (?,?)", ("w", "Tài liệu"))
    db.commit()
    backup = tmp_path / "backup.sqlite"
    copy_database(source, backup)
    restored = tmp_path / "restored.sqlite"
    copy_database(backup, restored)
    check = sqlite3.connect(restored)
    assert check.execute("SELECT name FROM workspaces WHERE id='w'").fetchone() == ("Tài liệu",)
    assert check.execute("PRAGMA integrity_check").fetchone() == ("ok",)
    check.close()
    with pytest.raises(BackupError, match="DESTINATION_EXISTS"):
        copy_database(source, restored)
    assert sqlite3.connect(restored).execute("SELECT name FROM workspaces").fetchone() == ("Tài liệu",)
    db.close()

def test_corrupt_source_does_not_leave_partial_backup(tmp_path):
    source = tmp_path / "corrupt.sqlite"
    source.write_bytes(b"not a sqlite database")
    output = tmp_path / "backup.sqlite"
    with pytest.raises(BackupError, match="SOURCE_INVALID"):
        copy_database(source, output)
    assert not output.exists()

def test_missing_source_does_not_create_backup(tmp_path):
    output = tmp_path / "backup.sqlite"
    with pytest.raises(BackupError, match="SOURCE_INVALID"):
        copy_database(tmp_path / "missing.sqlite", output)
    assert not output.exists()


def test_backup_and_restore_commands(tmp_path):
    import os
    import subprocess
    source = tmp_path / "data.sqlite"
    db = connect(source)
    migrate(db)
    db.execute("INSERT INTO workspaces(id,name) VALUES ('w','Test')")
    db.commit()
    db.close()
    api = Path(__file__).resolve().parents[1] / "apps" / "api"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    backup = tmp_path / "backup.sqlite"
    restored = tmp_path / "restore.sqlite"
    def run(*args):
        return subprocess.run([sys.executable, "-m", "localpdf.cli", *map(str, args)], cwd=api, env=env, capture_output=True, text=True)
    assert run("--db", source, "backup", "--to", backup).returncode == 0
    assert run("--db", restored, "restore", "--from", backup).returncode == 0
    assert run("--db", restored, "restore", "--from", backup).returncode != 0
    db = sqlite3.connect(restored)
    assert db.execute("SELECT name FROM workspaces WHERE id='w'").fetchone() == ("Test",)
    db.close()
