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


def test_source_changed_during_registration_rolls_back(tmp_path, database):
    source = tmp_path / "synthetic.pdf"
    synthetic_pdf(source)
    def mutate_fixture():
        # Simulate an independent process changing this synthetic fixture.
        with source.open("ab") as stream:
            stream.write(b"changed externally")
        return 0
    database.create_function("mutate_fixture", 0, mutate_fixture)
    database.execute("CREATE TRIGGER test_external_change BEFORE INSERT ON file_assets BEGIN SELECT mutate_fixture(); END")
    database.commit()
    with pytest.raises(ImportFailure, match="SOURCE_CHANGED"):
        import_pdf(database, "w", source)
    assert database.execute("SELECT count(*) FROM file_assets").fetchone()[0] == 0
    assert database.execute("SELECT count(*) FROM documents").fetchone()[0] == 0
    assert database.execute("SELECT count(*) FROM document_versions").fetchone()[0] == 0


def test_source_path_replaced_before_commit_rolls_back(tmp_path, database, monkeypatch):
    import os
    import types
    source = tmp_path / "synthetic.pdf"
    synthetic_pdf(source)
    real_stat = os.stat
    def simulate_replacement():
        def changed_stat(path, *args, **kwargs):
            result = real_stat(path, *args, **kwargs)
            if Path(path) == source:
                return types.SimpleNamespace(st_dev=result.st_dev, st_ino=result.st_ino + 1, st_size=result.st_size)
            return result
        monkeypatch.setattr(os, "stat", changed_stat)
        return 0
    database.create_function("replace_fixture_path", 0, simulate_replacement)
    database.execute("CREATE TRIGGER test_external_replacement BEFORE INSERT ON file_assets BEGIN SELECT replace_fixture_path(); END")
    database.commit()
    with pytest.raises(ImportFailure, match="SOURCE_CHANGED"):
        import_pdf(database, "w", source)
    assert database.execute("SELECT count(*) FROM documents").fetchone()[0] == 0
