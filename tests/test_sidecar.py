import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API = Path(__file__).resolve().parents[1] / "apps" / "api"

def test_sidecar_starts_authenticated_and_stops_on_parent_eof():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("LOCALPDF_SESSION_TOKEN", None)
    process = subprocess.Popen([sys.executable, "-m", "localpdf.sidecar"], cwd=API, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    token = "s" * 40
    try:
        process.stdin.write(token + "\n")
        process.stdin.flush()
        import queue
        import threading
        lines = queue.Queue()
        threading.Thread(target=lambda: lines.put(process.stdout.readline()), daemon=True).start()
        ready = json.loads(lines.get(timeout=10))
        assert ready["host"] == "127.0.0.1"
        url = "http://127.0.0.1:" + str(ready["port"]) + "/api/v1/health"
        for _ in range(100):
            try:
                with urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization":"Bearer " + token}), timeout=1) as response:
                    assert response.status == 200
                    break
            except (urllib.error.URLError, TimeoutError):
                time.sleep(.05)
        else:
            raise AssertionError("sidecar did not start")
        try:
            urllib.request.urlopen(url, timeout=1)
            raise AssertionError("unauthenticated request succeeded")
        except urllib.error.HTTPError as exc:
            assert exc.code == 401
        process.stdin.close()
        process.wait(timeout=10)
        assert process.returncode == 0
        assert token not in process.stdout.read()
        assert token not in process.stderr.read()
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=5)

def test_sidecar_rejects_short_token():
    result = subprocess.run([sys.executable, "-m", "localpdf.sidecar"], cwd=API, input="short\n", capture_output=True, text=True, timeout=10)
    assert result.returncode == 2
    assert "short" not in result.stdout + result.stderr


def test_workspace_persists_across_sidecar_restart(tmp_path):
    import sqlite3
    import queue
    import threading
    sys.path.insert(0, str(API))
    from localpdf.storage import connect, migrate
    db_path = tmp_path / "workspace.sqlite"
    db = connect(db_path)
    migrate(db)
    db.close()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", LOCALPDF_DB_PATH=str(db_path))
    token = "r" * 40
    def run_once(create):
        process = subprocess.Popen([sys.executable, "-m", "localpdf.sidecar"], cwd=API, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            process.stdin.write(token + "\n")
            process.stdin.flush()
            lines = queue.Queue()
            threading.Thread(target=lambda: lines.put(process.stdout.readline()), daemon=True).start()
            ready = json.loads(lines.get(timeout=10))
            url = "http://127.0.0.1:" + str(ready["port"]) + "/api/v1/workspaces"
            headers = {"Authorization":"Bearer " + token, "Content-Type":"application/json"}
            for _ in range(100):
                try:
                    health = urllib.request.Request(url.rsplit("/", 1)[0] + "/health", headers=headers)
                    with urllib.request.urlopen(health, timeout=1) as response:
                        if response.status == 200:
                            break
                except (urllib.error.URLError, TimeoutError):
                    time.sleep(.05)
            else:
                raise AssertionError("sidecar did not start")
            request = urllib.request.Request(url, headers=headers, data=b'{"name":"Test"}' if create else None)
            with urllib.request.urlopen(request, timeout=5) as response:
                return json.load(response)
        finally:
            process.stdin.close()
            try: process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
    created = run_once(True)
    after_restart = run_once(False)
    assert after_restart[0]["id"] == created["id"]
    with sqlite3.connect(db_path) as db:
        assert db.execute("SELECT count(*) FROM workspaces").fetchone()[0] == 1
