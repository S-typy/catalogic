"""Интеграционные тесты: скан и поиск."""

from __future__ import annotations

from pathlib import Path

from catalogic.app import run_scan
from catalogic.storage import open_sqlite_storage


def test_scan_to_sqlite_and_wildcard_search(tmp_path: Path) -> None:
    data_root = tmp_path / "root"
    data_root.mkdir()
    (data_root / "photo_01.jpg").write_text("a")
    (data_root / "photo_02.jpg").write_text("b")
    (data_root / "notes.txt").write_text("c")

    db_path = tmp_path / "catalogic.db"
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        scan_root = storage.scan_roots.get_or_create(str(data_root))
        assert scan_root.id is not None
        root_id = int(scan_root.id)

        run_scan(
            data_root,
            sink=lambda record: storage.files.upsert(root_id, record),
        )

        wildcard = storage.files.search_by_wildcard("photo_0?.jpg")
        assert len(wildcard) == 2
        names = sorted(record.name for record in wildcard)
        assert names == ["photo_01.jpg", "photo_02.jpg"]
    finally:
        storage.close()
