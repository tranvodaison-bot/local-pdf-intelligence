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
        while sys.stdin.buffer.read(1):
            pass
        server.should_exit = True
    threading.Thread(target=monitor_parent, daemon=True).start()
    print(json.dumps({"host":"127.0.0.1", "port":sock.getsockname()[1]}), flush=True)
    try:
        server.run(sockets=[sock])
    finally:
        sock.close()
        os.environ.pop("LOCALPDF_SESSION_TOKEN", None)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
