"""Data-plane worker: выполняет скан по команде из БД."""

from __future__ import annotations

import os
import socket
import time

from catalogic.app.scan import run_scan
from catalogic.storage import open_sqlite_storage


class ScannerWorker:
    """Scanner process worker."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._pid = os.getpid()
        self._host = socket.gethostname()

    def run_forever(self, *, poll_interval_sec: float = 1.0) -> None:
        while True:
            did_work = self.run_pending_once()
            if not did_work:
                time.sleep(poll_interval_sec)

    def run_pending_once(self) -> bool:
        storage = open_sqlite_storage(self._db_path, migrate=True)
        try:
            storage.scan_state.touch_worker_heartbeat(pid=self._pid, host=self._host)
            status = storage.scan_state.get()
            if status["desired_state"] != "running":
                return False

            roots = [root for root in storage.scan_roots.list_all() if root.id is not None]
            if not roots:
                storage.scan_state.set_finished(
                    state="idle",
                    desired_state="idle",
                    message="No roots configured",
                )
                return True

            follow_symlinks = bool(status.get("follow_symlinks"))
            storage.scan_state.set_running(current_root=roots[0].path, message="Scanner is running")
            total_processed = 0
            total_emitted = 0
            total_skipped = 0

            for root in roots:
                root_id = int(root.id)
                last_check_at = 0.0
                should_stop_cached = False

                def _sink(record) -> None:
                    storage.files.upsert(root_id, record)

                def _should_stop() -> bool:
                    nonlocal last_check_at, should_stop_cached
                    now = time.time()
                    if now - last_check_at < 0.5:
                        return should_stop_cached
                    state = storage.scan_state.get()
                    should_stop_cached = state["desired_state"] != "running"
                    last_check_at = now
                    return should_stop_cached

                def _progress(stats) -> None:
                    storage.scan_state.update_progress(
                        processed_files=total_processed + stats.files_discovered,
                        emitted_records=total_emitted + stats.records_emitted,
                        skipped_files=total_skipped + stats.skipped_files,
                        current_root=root.path,
                    )

                stats = run_scan(
                    root.path,
                    follow_symlinks=follow_symlinks,
                    sink=_sink,
                    should_stop=_should_stop,
                    on_progress=_progress,
                )
                total_processed += stats.files_discovered
                total_emitted += stats.records_emitted
                total_skipped += stats.skipped_files

                storage.scan_state.update_progress(
                    processed_files=total_processed,
                    emitted_records=total_emitted,
                    skipped_files=total_skipped,
                    current_root=root.path,
                )
                if stats.interrupted:
                    storage.scan_state.set_finished(
                        state="stopped",
                        desired_state="stopped",
                        message="Scan stopped by user",
                    )
                    return True

            storage.scan_state.set_finished(
                state="idle",
                desired_state="idle",
                message="Scan finished",
            )
            return True
        except Exception as e:
            storage.scan_state.set_finished(
                state="failed",
                desired_state="idle",
                message=str(e),
            )
            return True
        finally:
            storage.close()
