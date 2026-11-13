"""Explicit local-only maintenance interface; not a desktop file-picker replacement."""
import argparse
import json
import sqlite3
from pathlib import Path
from .importer import ImportFailure, import_pdf
from .backup import BackupError, copy_database
from .storage import connect, migrate

def main():
    parser = argparse.ArgumentParser(description="Local PDF registration")
    parser.add_argument("--db", required=True, help="Absolute path to local application database")
    commands = parser.add_subparsers(dest="command", required=True)
    setup = commands.add_parser("init-workspace")
    setup.add_argument("--id", required=True)
    setup.add_argument("--name", required=True)
    add = commands.add_parser("import")
    add.add_argument("--workspace", required=True)
    add.add_argument("--file", required=True, help="Absolute path selected by local user")
    backup = commands.add_parser("backup")
    backup.add_argument("--to", required=True, help="New absolute backup path")
    restore = commands.add_parser("restore")
    restore.add_argument("--from", dest="backup_source", required=True, help="Existing absolute backup path")
    args = parser.parse_args()
    if not Path(args.db).is_absolute():
        parser.error("--db must be absolute")
    db_path = Path(args.db)
    if db_path.suffix.lower() == ".pdf" or (args.command == "import" and db_path.resolve() == Path(args.file).resolve()):
        parser.error("database path must not be the source PDF")
    if args.command in ("backup", "restore"):
        source = db_path if args.command == "backup" else Path(args.backup_source)
        destination = Path(args.to) if args.command == "backup" else db_path
        if destination.suffix.lower() == ".pdf":
            parser.error("backup destination must not be a PDF")
        try:
            copy_database(source, destination)
            print(json.dumps({"status": "created", "operation": args.command}))
            return 0
        except BackupError as exc:
            print(json.dumps({"status": "error", "code": str(exc)}))
            return 1
    if db_path.exists():
        with db_path.open("rb") as existing:
            if existing.read(16) != b"SQLite format 3\x00":
                parser.error("existing database must be a SQLite file")
    db = connect(db_path)
    try:
        migrate(db)
        if args.command == "init-workspace":
            db.execute("INSERT INTO workspaces(id,name) VALUES (?,?)", (args.id,args.name))
            db.commit()
            result = {"status":"created", "workspace_id":args.id}
        else:
            result = import_pdf(db, args.workspace, args.file)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (ImportFailure, sqlite3.Error, RuntimeError) as exc:
        db.rollback()
        # Do not print paths, document contents or a traceback into logs.
        code = str(exc) if isinstance(exc, ImportFailure) else "DATABASE_ERROR"
        print(json.dumps({"status":"error", "code":code}, ensure_ascii=False))
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    raise SystemExit(main())
