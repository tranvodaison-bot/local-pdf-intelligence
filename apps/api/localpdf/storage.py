"""SQLite migrations; no automatic adoption of pre-existing schemas."""
import hashlib
import sqlite3
from pathlib import Path

MIGRATION = Path(__file__).resolve().parents[3] / "db" / "001_initial.sql"

def connect(path):
    db = sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=5000")
    return db

def migrate(db, sql_path=MIGRATION):
    raw = Path(sql_path).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    exists = db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='migration_checksums'").fetchone()
    if exists:
        row = db.execute("SELECT sha256 FROM migration_checksums WHERE version=1").fetchone()
        if row:
            if row[0] != digest:
                raise RuntimeError("Applied migration checksum differs")
            return False
    elif db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' LIMIT 1").fetchone():
        raise RuntimeError("Existing database requires reviewed adoption; refusing migration")
    if db.in_transaction:
        raise RuntimeError("Migration requires an idle connection")
    try:
        db.execute("BEGIN IMMEDIATE")
        db.execute("CREATE TABLE IF NOT EXISTS migration_checksums (version INTEGER PRIMARY KEY, sha256 TEXT NOT NULL)")
        statement = ""
        for line in raw.decode("utf-8-sig").splitlines(keepends=True):
            statement += line
            if sqlite3.complete_statement(statement):
                db.execute(statement)
                statement = ""
        if statement.strip():
            raise ValueError("Incomplete migration SQL")
        db.execute("INSERT INTO migration_checksums VALUES (?, ?)", (1, digest))
        db.commit()
        return True
    except BaseException:
        db.rollback()
        raise
