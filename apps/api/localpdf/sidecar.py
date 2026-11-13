"""Local sidecar process protocol; parent must keep stdin open for its lifetime.

First line: ASCII session token; stdout: one JSON line with loopback port.
No token is passed in argv or emitted to stdout/stderr. EOF stops the server.
"""
import json
import os
import socket
import sys
import threading
import uvicorn

from .main import app
from .capabilities import InvalidCapability, grants

def main():
    line = sys.stdin.buffer.readline(4097)
    try:
        token = line.rstrip(b"\r\n").decode("ascii")
    except UnicodeDecodeError:
        return 2
    if len(line) > 4096 or len(token) < 32 or not token.isprintable() or any(c.isspace() for c in token):
        return 2
    os.environ["LOCALPDF_SESSION_TOKEN"] = token
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    sock.listen(128)
    config = uvicorn.Config(app, host="127.0.0.1", log_config=None, access_log=False)
    server = uvicorn.Server(config)
    def monitor_parent():
        while True:
            line = sys.stdin.buffer.readline(65537)
            if not line or len(line) > 65536:
                break
            request_id = None
            try:
                request = json.loads(line)
                if not isinstance(request, dict) or request.get("op") != "grant":
                    raise ValueError("unsupported command")
                request_id = request.get("request_id")
                if not isinstance(request_id, str) or len(request_id) > 64:
                    raise ValueError("invalid request id")
                capability = grants.issue(request.get("path"), request.get("workspace_id"))
                response = {"request_id":request_id, "capability":capability}
            except (ValueError, TypeError, InvalidCapability):
                response = {"request_id":request_id, "error":"GRANT_INVALID"}
            print(json.dumps(response), flush=True)
        server.should_exit = True
    print(json.dumps({"host":"127.0.0.1", "port":sock.getsockname()[1]}), flush=True)
    threading.Thread(target=monitor_parent, daemon=True).start()
    try:
        server.run(sockets=[sock])
    finally:
        sock.close()
        os.environ.pop("LOCALPDF_SESSION_TOKEN", None)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
