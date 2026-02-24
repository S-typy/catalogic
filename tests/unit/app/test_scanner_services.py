"""Тесты разделения scanner control-plane и worker."""

from __future__ import annotations

from pathlib import Path

from catalogic.app import ScannerService, ScannerWorker
from catalogic.app import scanner_worker as scanner_worker_module
from catalogic.storage import open_sqlite_storage
from catalogic.storage.repositories.sqlite import SQLiteScanStateRepository


def test_scanner_service_and_worker_cycle(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    data_root.mkdir()
    (data_root / "a.txt").write_text("aa")

    db_path = tmp_path / "catalogic.db"
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        storage.scan_roots.get_or_create(str(data_root))
    finally:
        storage.close()

    service = ScannerService(str(db_path))
    worker = ScannerWorker(str(db_path))

    started = service.start([str(data_root)])
    assert started.started is True

    pre = service.status()
    assert pre["desired_state"] == "running"

    assert worker.run_pending_once() is True
    post = service.status()
    assert post["state"] == "idle"
    assert post["desired_state"] == "idle"
    assert int(post["processed_files"]) >= 1
    assert post["worker_alive"] is True
    assert post["worker_pid"] is not None
    assert post["worker_host"] is not None


def test_worker_heartbeat_when_idle(tmp_path: Path) -> None:
    db_path = tmp_path / "catalogic.db"
    storage = open_sqlite_storage(db_path, migrate=True)
    storage.close()

    service = ScannerService(str(db_path))
    worker = ScannerWorker(str(db_path))

    assert worker.run_pending_once() is False
    status = service.status()
    assert status["state"] == "idle"
    assert status["desired_state"] == "idle"
    assert status["worker_alive"] is True


def test_worker_heartbeat_touched_during_progress(tmp_path: Path, monkeypatch) -> None:
    data_root = tmp_path / "data"
    data_root.mkdir()
    (data_root / "a.txt").write_text("aa")

    db_path = tmp_path / "catalogic.db"
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        storage.scan_roots.get_or_create(str(data_root))
    finally:
        storage.close()

    service = ScannerService(str(db_path))
    worker = ScannerWorker(str(db_path))
    assert service.start([str(data_root)]).started is True

    calls = {"count": 0}
    original_touch = SQLiteScanStateRepository.touch_worker_heartbeat

    def _touch(self, *, pid: int, host: str) -> None:  # type: ignore[no-untyped-def]
        calls["count"] += 1
        original_touch(self, pid=pid, host=host)

    class _Stats:
        files_discovered = 1
        records_emitted = 1
        skipped_files = 0
        interrupted = False

    def _fake_run_scan(root, *, follow_symlinks=False, sink=None, should_stop=None, on_progress=None):  # type: ignore[no-untyped-def]
        if on_progress is not None:
            on_progress(_Stats())
        return _Stats()

    monkeypatch.setattr(SQLiteScanStateRepository, "touch_worker_heartbeat", _touch)
    monkeypatch.setattr(scanner_worker_module, "run_scan", _fake_run_scan)

    assert worker.run_pending_once() is True
    # Один touch в начале run_pending_once + минимум один из _progress.
    assert calls["count"] >= 2
