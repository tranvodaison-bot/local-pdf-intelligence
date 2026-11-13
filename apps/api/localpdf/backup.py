"""Explicit local SQLite snapshots; source PDF assets are never copied or deleted."""
import os
import sqlite3
from pathlib import Path

class BackupError(Exception):
    pass

def copy_database(source, destination):
    """Copy a consistent SQLite snapshot to a new file; never replace a target."""
    source = Path(source)
    destination = Path(destination)
    if not source.is_absolute() or not destination.is_absolute() or ".." in source.parts or ".." in destination.parts:
        raise BackupError("PATH_INVALID")
    if not source.is_file() or source.is_symlink():
        raise BackupError("SOURCE_INVALID")
    for part in (destination, *destination.parents):
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise BackupError("PATH_LINK_REJECTED")
    input_db = None
    output_db = None
    identity = None
    success = False
    try:
        input_db = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
        if input_db.execute("PRAGMA integrity_check").fetchone() != ("ok",):
            raise BackupError("SOURCE_INVALID")
        try:
            fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError as exc:
            raise BackupError("DESTINATION_EXISTS") from exc
        try:
            stat = os.fstat(fd)
            identity = (stat.st_dev, stat.st_ino)
        finally:
            os.close(fd)
        output_db = sqlite3.connect(destination)
        input_db.backup(output_db)
        if output_db.execute("PRAGMA integrity_check").fetchone() != ("ok",):
            raise BackupError("BACKUP_INVALID")
        success = True
    except BackupError:
        raise
    except (sqlite3.Error, OSError) as exc:
        raise BackupError("SOURCE_INVALID" if identity is None else "BACKUP_FAILED") from exc
    finally:
        if output_db is not None:
            output_db.close()
        if input_db is not None:
            input_db.close()
        if identity is not None and not success:
            try:
                stat = os.stat(destination, follow_symlinks=False)
                if (stat.st_dev, stat.st_ino) == identity:
                    destination.unlink()
            except FileNotFoundError:
                pass
