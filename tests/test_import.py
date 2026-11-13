import hashlib
import sys
from pathlib import Path

import pytest
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "api"))
from localpdf.importer import ImportFailure, import_pdf
from localpdf.storage import connect, migrate

@pytest.fixture
def database(tmp_path):
    db = connect(tmp_path / "app.sqlite")
    migrate(db)
    db.execute("INSERT INTO workspaces(id,name) VALUES ('w','Workspace')")
    db.commit()
    yield db
    db.close()

def synthetic_pdf(path):
    pdf = canvas.Canvas(str(path))
    pdf.drawString(72, 720, "Synthetic test PDF")
    pdf.showPage()
    pdf.save()

def test_import_and_duplicate_do_not_modify_source(tmp_path, database):
    source = tmp_path / "Hồ sơ.pdf"
    synthetic_pdf(source)
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    result = import_pdf(database, "w", source)
    assert result["status"] == "imported"
    assert result["sha256"] == before
    assert database.execute("SELECT status FROM document_versions").fetchone()[0] == "PENDING"
    assert import_pdf(database, "w", source)["status"] == "duplicate"
    assert database.execute("SELECT count(*) FROM documents").fetchone()[0] == 1
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before

def test_rejects_bad_header_and_path_traversal(tmp_path, database):
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"not a PDF")
    with pytest.raises(ImportFailure, match="PDF_HEADER_INVALID"):
        import_pdf(database, "w", bad)
    with pytest.raises(ImportFailure, match="PATH_INVALID"):
        import_pdf(database, "w", tmp_path / "sub" / ".." / "bad.pdf")
    assert database.execute("SELECT count(*) FROM documents").fetchone()[0] == 0

def test_rejects_malformed_and_missing_workspace(tmp_path, database):
    bad = tmp_path / "bad.pdf"
    bad.write_bytes(b"%PDF-1.7\ninvalid")
    with pytest.raises(ImportFailure, match="PDF_INVALID"):
        import_pdf(database, "w", bad)
    good = tmp_path / "good.pdf"
    synthetic_pdf(good)
    with pytest.raises(ImportFailure, match="WORKSPACE_NOT_FOUND"):
        import_pdf(database, "unknown", good)
    assert database.execute("SELECT count(*) FROM documents").fetchone()[0] == 0


def test_cli_rejects_source_as_database(tmp_path):
    import os
    import subprocess
    source = tmp_path / "source.pdf"
    synthetic_pdf(source)
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    api = Path(__file__).resolve().parents[1] / "apps" / "api"
    result = subprocess.run([sys.executable, "-m", "localpdf.cli", "--db", str(source), "import", "--workspace", "w", "--file", str(source)], cwd=api, env=env, capture_output=True, text=True)
    assert result.returncode != 0
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before

def test_rejects_password_pdf(tmp_path, database):
    from pypdf import PdfWriter
    source = tmp_path / "locked.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.encrypt("password")
    with source.open("wb") as output:
        writer.write(output)
    with pytest.raises(ImportFailure, match="PDF_PASSWORD_REQUIRED"):
        import_pdf(database, "w", source)
    assert database.execute("SELECT count(*) FROM documents").fetchone()[0] == 0


def test_local_cli_import_smoke(tmp_path):
    import json
    import os
    import subprocess
    source = tmp_path / "Tài liệu.pdf"
    synthetic_pdf(source)
    original = hashlib.sha256(source.read_bytes()).hexdigest()
    api = Path(__file__).resolve().parents[1] / "apps" / "api"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    prefix = [sys.executable, "-m", "localpdf.cli", "--db", str(tmp_path / "local.sqlite")]
    created = subprocess.run(prefix + ["init-workspace", "--id", "w", "--name", "Kiểm thử"], cwd=api, env=env, capture_output=True, text=True, encoding="utf-8")
    assert created.returncode == 0, created.stderr
    added = subprocess.run(prefix + ["import", "--workspace", "w", "--file", str(source)], cwd=api, env=env, capture_output=True, text=True, encoding="utf-8")
    assert added.returncode == 0, added.stderr
    result = json.loads(added.stdout)
    assert result["status"] == "imported" and result["sha256"] == original
    assert hashlib.sha256(source.read_bytes()).hexdigest() == original
