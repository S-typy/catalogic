"""Control-plane сервис сканера (без выполнения скана в этом процессе)."""

from __future__ import annotations

from dataclasses import dataclass
import os
import socket
import time

from catalogic.storage import open_sqlite_storage


@dataclass(slots=True)
class StartScanResult:
    started: bool
    message: str


class ScannerService:
    """
    Backend-оркестратор.

    Пишет команды в БД (`desired_state`), исполняет их отдельный scanner-service процесс.
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    def start(self, roots: list[str], *, follow_symlinks: bool = False) -> StartScanResult:
        normalized = [root for root in roots if root]
        if not normalized:
            return StartScanResult(started=False, message="No roots configured")

        storage = open_sqlite_storage(self._db_path, migrate=True)
        try:
            status = storage.scan_state.get()
            if status["state"] == "running" or status["desired_state"] == "running":
                return StartScanResult(started=False, message="Scanner already running")
            storage.scan_state.set_desired_state(
                desired_state="running",
                follow_symlinks=follow_symlinks,
                message="Start requested",
            )
            return StartScanResult(started=True, message="Start requested")
        finally:
            storage.close()

    def stop(self) -> StartScanResult:
        storage = open_sqlite_storage(self._db_path, migrate=True)
        try:
            status = storage.scan_state.get()
            if status["state"] != "running" and status["desired_state"] != "running":
                return StartScanResult(started=False, message="Scanner is not running")
            storage.scan_state.set_desired_state(
                desired_state="stopped",
                message="Stop requested",
            )
            return StartScanResult(started=True, message="Stop requested")
        finally:
            storage.close()

    def is_running(self) -> bool:
        status = self.status()
        return bool(status.get("state") == "running")

    def status(self) -> dict[str, object]:
        storage = open_sqlite_storage(self._db_path, migrate=True)
        try:
            state = storage.scan_state.get()
        finally:
            storage.close()
        state["is_running"] = state.get("state") == "running"

        last_seen = state.get("worker_last_seen")
        stale_sec: float | None
        if isinstance(last_seen, (int, float)):
            stale_sec = max(0.0, time.time() - float(last_seen))
        else:
            stale_sec = None

        heartbeat_alive = stale_sec is not None and stale_sec <= 5.0
        pid_alive = self._is_worker_pid_alive_local(
            pid=state.get("worker_pid"),
            host=state.get("worker_host"),
        )
        state["worker_stale_sec"] = stale_sec
        state["worker_alive"] = heartbeat_alive or pid_alive
        state["worker_pid_alive"] = pid_alive
        return state

    @staticmethod
    def _is_worker_pid_alive_local(pid: object, host: object) -> bool:
        if not isinstance(pid, int) or pid <= 0:
            return False
        if not isinstance(host, str) or host != socket.gethostname():
            return False
        try:
            os.kill(pid, 0)
            return True
        except ProcessLookupError:
            return False
        except PermissionError:
            # Процесс существует, но нет прав на сигнал.
            return True
