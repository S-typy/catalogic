"""Control-plane сервис сканера (без выполнения скана в этом процессе)."""

from __future__ import annotations

from dataclasses import dataclass
import os
import shutil
import socket
import sys
import time
from typing import Any

from catalogic.scanner.hash_util import describe_hash_policy
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
        self._cpu_snapshot: dict[int, tuple[float, float]] = {}

    def start(
        self,
        roots: list[str],
        *,
        follow_symlinks: bool = False,
        scan_mode: str = "add_new",
    ) -> StartScanResult:
        normalized = [root for root in roots if root]
        if not normalized:
            return StartScanResult(started=False, message="No roots configured")
        mode = scan_mode if scan_mode in {"rebuild", "add_new"} else "add_new"

        storage = open_sqlite_storage(self._db_path, migrate=True)
        try:
            status = storage.scan_state.get()
            if status["state"] == "running" or status["desired_state"] == "running":
                return StartScanResult(started=False, message="Scanner already running")
            storage.scan_state.set_desired_state(
                desired_state="running",
                follow_symlinks=follow_symlinks,
                scan_mode=mode,
                message=f"Start requested ({mode})",
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
        state["duration_sec"] = self._scan_duration_sec(state)
        processed = int(state.get("processed_files") or 0)
        duration = float(state.get("duration_sec") or 0.0)
        state["avg_sec_per_file"] = (duration / processed) if processed > 0 else None
        return state

    def diagnostics(self) -> dict[str, object]:
        status = self.status()
        storage = open_sqlite_storage(self._db_path, migrate=True)
        try:
            scanner_settings = storage.app_settings.get()
        finally:
            storage.close()
        process = self._read_process_metrics(
            pid=status.get("worker_pid"),
            host=status.get("worker_host"),
        )
        return {
            "scan": status,
            "process": process,
            "utilities": self._detect_utilities(scanner_settings),
            "scanner_settings": scanner_settings,
            "metrics": {
                "processed_files": int(status.get("processed_files") or 0),
                "emitted_records": int(status.get("emitted_records") or 0),
                "skipped_files": int(status.get("skipped_files") or 0),
                "skipped_existing_files": int(status.get("skipped_existing_files") or 0),
                "processed_image_files": int(status.get("processed_image_files") or 0),
                "processed_video_files": int(status.get("processed_video_files") or 0),
                "processed_audio_files": int(status.get("processed_audio_files") or 0),
                "processed_other_files": int(status.get("processed_other_files") or 0),
                "avg_sec_per_file": status.get("avg_sec_per_file"),
            },
        }

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

    @staticmethod
    def _scan_duration_sec(state: dict[str, Any]) -> float | None:
        started = state.get("started_at")
        if not isinstance(started, (int, float)):
            return None
        finished = state.get("finished_at")
        end = float(finished) if isinstance(finished, (int, float)) else time.time()
        return max(0.0, end - float(started))

    @staticmethod
    def _detect_utilities(scanner_settings: dict[str, Any] | None = None) -> dict[str, object]:
        def _has_module(name: str) -> bool:
            try:
                __import__(name)
                return True
            except Exception:
                return False

        ffprobe_path = shutil.which("ffprobe")
        return {
            "ffprobe_available": bool(ffprobe_path),
            "ffprobe_path": ffprobe_path,
            "python_magic_available": _has_module("magic"),
            "pillow_available": _has_module("PIL"),
            "python_version": sys.version.split()[0],
            **describe_hash_policy(scanner_settings),
        }

    def _read_process_metrics(self, *, pid: object, host: object) -> dict[str, object]:
        if not self._is_worker_pid_alive_local(pid=pid, host=host):
            return {"alive": False}
        if not isinstance(pid, int):
            return {"alive": False}

        now = time.time()
        try:
            with open(f"/proc/{pid}/stat", "r", encoding="utf-8") as f:
                stat_raw = f.read().strip()
            with open("/proc/uptime", "r", encoding="utf-8") as f:
                uptime_raw = f.read().strip().split()[0]
            rss_bytes = self._read_rss_bytes(pid)
        except OSError:
            return {"alive": True, "pid": pid, "error": "Cannot read /proc metrics"}

        right = stat_raw.rfind(")")
        if right < 0 or right + 2 >= len(stat_raw):
            return {"alive": True, "pid": pid, "error": "Unexpected /proc stat format"}
        fields = stat_raw[right + 2 :].split()
        if len(fields) < 22:
            return {"alive": True, "pid": pid, "error": "Unexpected /proc stat format"}

        clk_tck = os.sysconf("SC_CLK_TCK")
        # После pid/comm/state индексация смещена относительно raw /proc stat.
        proc_cpu_sec = (float(fields[11]) + float(fields[12])) / float(clk_tck)
        proc_start_sec = float(fields[19]) / float(clk_tck)
        sys_uptime_sec = float(uptime_raw)
        proc_uptime_sec = max(0.0, sys_uptime_sec - proc_start_sec)

        prev = self._cpu_snapshot.get(pid)
        cpu_percent: float | None = None
        if prev is not None:
            prev_cpu, prev_wall = prev
            wall_delta = max(0.0, now - prev_wall)
            cpu_delta = max(0.0, proc_cpu_sec - prev_cpu)
            if wall_delta > 0:
                cpu_percent = (cpu_delta / wall_delta) * 100.0
        self._cpu_snapshot[pid] = (proc_cpu_sec, now)

        return {
            "alive": True,
            "pid": pid,
            "cpu_percent": cpu_percent,
            "cpu_time_sec": proc_cpu_sec,
            "memory_rss_bytes": rss_bytes,
            "uptime_sec": proc_uptime_sec,
        }

    @staticmethod
    def _read_rss_bytes(pid: int) -> int | None:
        try:
            with open(f"/proc/{pid}/status", "r", encoding="utf-8") as f:
                for line in f:
                    if not line.startswith("VmRSS:"):
                        continue
                    parts = line.split()
                    if len(parts) >= 2:
                        return int(parts[1]) * 1024
        except OSError:
            return None
        return None
