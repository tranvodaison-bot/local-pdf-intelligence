"""Ephemeral one-use selection grants, issued only over the trusted control pipe."""
import secrets
import threading
import time
from pathlib import Path

class InvalidCapability(Exception):
    pass

class SelectionGrants:
    def __init__(self, ttl=60.0, clock=time.monotonic, max_grants=256):
        self._ttl, self._clock, self._max = ttl, clock, max_grants
        self._lock = threading.Lock()
        self._items = {}

    def issue(self, path, workspace_id):
        if not isinstance(path, str) or not isinstance(workspace_id, str) or not workspace_id or len(workspace_id) > 128:
            raise InvalidCapability("GRANT_INVALID")
        selected = Path(path)
        if not selected.is_absolute() or ".." in selected.parts:
            raise InvalidCapability("GRANT_INVALID")
        with self._lock:
            now = self._clock()
            self._items = {key:value for key,value in self._items.items() if value[2] > now}
            if len(self._items) >= self._max:
                raise InvalidCapability("GRANT_LIMIT")
            token = secrets.token_urlsafe(32)
            self._items[token] = (str(selected), workspace_id, now + self._ttl)
            return token

    def consume(self, token, workspace_id):
        if not isinstance(token, str) or len(token) > 128:
            raise InvalidCapability("CAPABILITY_INVALID")
        with self._lock:
            grant = self._items.pop(token, None)
            if not grant or grant[2] <= self._clock() or grant[1] != workspace_id:
                raise InvalidCapability("CAPABILITY_INVALID")
            return grant[0]

grants = SelectionGrants()
