"""Bridge-session-owned lifecycle for the loopback router listener."""

from __future__ import annotations

import socket
import threading
import time
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any

from modules.foundation.errors import ValidationError
from modules.router.activity import ActivityLog
from modules.router.policy import RouterPolicyService
from modules.router.server import _make_handler

_LOOPBACK = {"127.0.0.1"}


class RouterRuntimeService:
    def __init__(self, state_dir: Path, policy: RouterPolicyService | None = None) -> None:
        self.policy = policy or RouterPolicyService(state_dir)
        self.activity = ActivityLog()
        self._lock = threading.RLock()
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self._host: str | None = None
        self._port: int | None = None
        self._started_at: int | None = None
        self._error: str | None = None

    @staticmethod
    def _validate_host(host: object) -> str:
        if host not in _LOOPBACK:
            raise ValidationError("router-bind-rejected", "Router may bind only to loopback.")
        return str(host)

    @staticmethod
    def _validate_port(port: object) -> int:
        if not isinstance(port, int) or isinstance(port, bool) or not 1 <= port <= 65535:
            raise ValidationError("invalid-router-port", "Router port must be between 1 and 65535.")
        return port

    def status(self) -> dict[str, Any]:
        with self._lock:
            running = self._thread is not None and self._thread.is_alive()
            return {
                "running": running,
                "host": self._host if running else None,
                "port": self._port if running else None,
                "started_at": self._started_at if running else None,
                "error": self._error,
            }

    def start(self, host: object = "127.0.0.1", port: object = 15721) -> dict[str, Any]:
        bind_host = self._validate_host(host)
        bind_port = self._validate_port(port)
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                raise ValidationError("router-already-running", "Router listener is already running.")
            try:
                server = ThreadingHTTPServer((bind_host, bind_port), _make_handler(self.policy, self.activity))
            except OSError as error:
                raise ValidationError("router-port-unavailable", "Router listener port is unavailable.") from error
            self._server = server
            self._host = bind_host
            self._port = bind_port
            self._started_at = int(time.time())
            self._error = None
            self._thread = threading.Thread(target=self._serve, name="modeltoolbox-router", daemon=True)
            self._thread.start()
            return self.status()

    def _serve(self) -> None:
        server = self._server
        if server is None:
            return
        try:
            server.serve_forever(poll_interval=0.2)
        except Exception:
            with self._lock:
                self._error = "Router listener stopped unexpectedly."
        finally:
            server.server_close()

    def stop(self) -> dict[str, Any]:
        with self._lock:
            server = self._server
            thread = self._thread
            if server is None or thread is None or not thread.is_alive():
                raise ValidationError("router-not-running", "Router listener is not running.")
            server.shutdown()
        thread.join(timeout=2)
        with self._lock:
            self._server = None
            self._thread = None
            self._host = None
            self._port = None
            self._started_at = None
            return self.status()

    def activity_list(self) -> dict[str, Any]:
        return self.activity.list()
