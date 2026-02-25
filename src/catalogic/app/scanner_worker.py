"""Data-plane worker: выполняет скан по команде из БД."""

from __future__ import annotations

import os
from pathlib import Path
import socket
import time
from typing import Any, Callable

from catalogic.app.scan import run_scan
from catalogic.scanner import ScanStats, iterate_files
from catalogic.scanner.metadata import get_file_record, get_file_record_with_cached_md5
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
            scan_mode = str(status.get("scan_mode") or "add_new")
            if scan_mode not in {"rebuild", "add_new"}:
                scan_mode = "add_new"
            if scan_mode == "rebuild":
                storage.files.delete_all()

            storage.scan_state.set_running(current_root=roots[0].path, message="Scanner is running")
            total_processed = 0
            total_emitted = 0
            total_skipped = 0
            total_image = 0
            total_video = 0
            total_audio = 0
            total_other = 0
            total_skipped_existing = 0

            for root in roots:
                root_id = int(root.id)
                last_check_at = 0.0
                should_stop_cached = False

                def _sink(record) -> None:
                    nonlocal total_image, total_video, total_audio, total_other
                    storage.files.upsert(root_id, record)
                    category = self._mime_category(record.mime)
                    if category == "image":
                        total_image += 1
                    elif category == "video":
                        total_video += 1
                    elif category == "audio":
                        total_audio += 1
                    else:
                        total_other += 1

                def _should_stop() -> bool:
                    nonlocal last_check_at, should_stop_cached
                    now = time.time()
                    if now - last_check_at < 0.5:
                        return should_stop_cached
                    state = storage.scan_state.get()
                    should_stop_cached = state["desired_state"] != "running"
                    last_check_at = now
                    return should_stop_cached

                def _progress(stats: ScanStats) -> None:
                    storage.scan_state.touch_worker_heartbeat(pid=self._pid, host=self._host)
                    storage.scan_state.update_progress(
                        processed_files=total_processed + stats.files_discovered,
                        emitted_records=total_emitted + stats.records_emitted,
                        skipped_files=total_skipped + stats.skipped_files,
                        processed_image_files=total_image,
                        processed_video_files=total_video,
                        processed_audio_files=total_audio,
                        processed_other_files=total_other,
                        skipped_existing_files=total_skipped_existing,
                        current_root=root.path,
                    )

                def _counter(kind: str) -> None:
                    nonlocal total_image, total_video, total_audio, total_other, total_skipped_existing
                    if kind == "image":
                        total_image += 1
                    elif kind == "video":
                        total_video += 1
                    elif kind == "audio":
                        total_audio += 1
                    elif kind == "skipped_existing":
                        total_skipped_existing += 1
                    else:
                        total_other += 1

                if scan_mode == "add_new":
                    stats = self._run_add_new_scan(
                        storage=storage,
                        root_id=root_id,
                        root_path=root.path,
                        follow_symlinks=follow_symlinks,
                        should_stop=_should_stop,
                        on_progress=_progress,
                        on_counter=_counter,
                    )
                else:
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
                    processed_image_files=total_image,
                    processed_video_files=total_video,
                    processed_audio_files=total_audio,
                    processed_other_files=total_other,
                    skipped_existing_files=total_skipped_existing,
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

    @staticmethod
    def _mime_category(mime: str | None) -> str:
        value = (mime or "").lower()
        if value.startswith("image/"):
            return "image"
        if value.startswith("video/"):
            return "video"
        if value.startswith("audio/"):
            return "audio"
        return "other"

    @staticmethod
    def _entry_complete(entry: dict[str, Any]) -> bool:
        if not entry.get("md5"):
            return False
        mime = str(entry.get("mime") or "")
        if not mime:
            # Для неизвестного MIME считаем запись полной, если есть базовые поля.
            return True
        if mime.startswith("video/"):
            return bool(entry.get("has_video_meta"))
        if mime.startswith("audio/"):
            return bool(entry.get("has_audio_meta"))
        if mime.startswith("image/"):
            return bool(entry.get("has_image_meta"))
        return True

    def _run_add_new_scan(
        self,
        *,
        storage,
        root_id: int,
        root_path: str,
        follow_symlinks: bool,
        should_stop: Callable[[], bool],
        on_progress: Callable[[ScanStats], None] | None,
        on_counter: Callable[[str], None],
    ) -> ScanStats:
        stats = ScanStats(root=str(Path(root_path).resolve()))

        for path in iterate_files(root_path, follow_symlinks=follow_symlinks):
            if should_stop():
                stats.interrupted = True
                break

            stats.files_discovered += 1
            try:
                st = path.stat(follow_symlinks=True)
                current_size = int(st.st_size)
                current_mtime = float(st.st_mtime)
            except OSError:
                stats.skipped_files += 1
                if on_progress is not None:
                    on_progress(stats)
                continue

            entry = storage.files.get_scan_entry(root_id=root_id, path=str(path))
            is_unchanged = (
                entry is not None
                and int(entry.get("size", -1)) == current_size
                and float(entry.get("mtime", -1.0)) == current_mtime
            )

            if entry is not None and is_unchanged and self._entry_complete(entry):
                stats.skipped_files += 1
                on_counter("skipped_existing")
                if on_progress is not None:
                    on_progress(stats)
                continue

            cached_md5 = None
            cached_size = None
            cached_mtime = None
            if entry is not None and is_unchanged:
                cached_md5 = str(entry.get("md5") or "") or None
                cached_size = int(entry.get("size", -1))
                cached_mtime = float(entry.get("mtime", -1.0))

            record = get_file_record_with_cached_md5(
                path,
                cached_size=cached_size,
                cached_mtime=cached_mtime,
                cached_md5=cached_md5,
            )
            if record is None:
                record = get_file_record(path)
            if record is None:
                stats.skipped_files += 1
                if on_progress is not None:
                    on_progress(stats)
                continue

            storage.files.upsert(root_id, record)
            stats.records_emitted += 1
            category = self._mime_category(record.mime)
            on_counter(category)

            if on_progress is not None:
                on_progress(stats)

        stats.finished_at = time.time()
        return stats
