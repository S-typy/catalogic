"""Тесты SQLite storage и репозиториев."""

from pathlib import Path

from catalogic.core.entities import FileRecord
from catalogic.storage import apply_sqlite_migrations, connect_sqlite, open_sqlite_storage


def _record(path: Path, *, size: int, md5: str | None) -> FileRecord:
    return FileRecord(
        path=str(path),
        size=size,
        mtime=100.0,
        ctime=90.0,
        mime="text/plain",
        is_symlink=False,
        md5=md5,
    )


def test_migrations_create_initial_tables(tmp_path: Path) -> None:
    """После миграции присутствуют базовые таблицы."""
    db_path = tmp_path / "catalogic.db"
    conn = connect_sqlite(db_path)
    try:
        applied = apply_sqlite_migrations(conn)
        assert "001_initial.sql" in applied

        table_names = {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
        }
        assert "schema_migrations" in table_names
        assert "scan_roots" in table_names
        assert "files" in table_names
    finally:
        conn.close()


def test_sqlite_repositories_upsert_and_search(tmp_path: Path) -> None:
    """Upsert обновляет запись по (root_id, path), поиск возвращает актуальные данные."""
    db_path = tmp_path / "catalogic.db"
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        root = storage.scan_roots.get_or_create(str(tmp_path))
        assert root.id is not None

        file_path = tmp_path / "a.txt"
        storage.files.upsert(root.id, _record(file_path, size=2, md5="a" * 32))
        storage.files.upsert(root.id, _record(file_path, size=5, md5="b" * 32))

        assert storage.files.count_by_root(root.id) == 1
        found = storage.files.search_by_name("a.txt")
        assert len(found) == 1
        assert found[0].path == str(file_path)
        assert found[0].size == 5
        assert found[0].md5 == "b" * 32
    finally:
        storage.close()


def test_sqlite_list_directory_children(tmp_path: Path) -> None:
    db_path = tmp_path / "catalogic.db"
    data_root = tmp_path / "data"
    nested = data_root / "nested"
    nested.mkdir(parents=True)

    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        root = storage.scan_roots.get_or_create(str(data_root))
        assert root.id is not None

        storage.files.upsert(root.id, _record(data_root / "a.txt", size=1, md5=None))
        storage.files.upsert(root.id, _record(nested / "b.txt", size=2, md5=None))
        storage.files.upsert(root.id, _record(nested / "c.txt", size=3, md5=None))

        top = storage.files.list_directory_children(
            root_id=root.id,
            root_path=str(data_root),
            dir_path=str(data_root),
        )
        assert [item["name"] for item in top] == ["nested", "a.txt"]
        top_file = next(item for item in top if item["type"] == "file")
        assert isinstance(top_file["mtime"], float)

        nested_children = storage.files.list_directory_children(
            root_id=root.id,
            root_path=str(data_root),
            dir_path=str(nested),
        )
        assert [item["name"] for item in nested_children] == ["b.txt", "c.txt"]
        assert all(isinstance(item["mtime"], float) for item in nested_children)
    finally:
        storage.close()


def test_sqlite_get_file_by_root_and_path(tmp_path: Path) -> None:
    db_path = tmp_path / "catalogic.db"
    data_root = tmp_path / "data"
    data_root.mkdir(parents=True)
    file_path = data_root / "movie.mkv"

    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        root = storage.scan_roots.get_or_create(str(data_root))
        assert root.id is not None
        storage.files.upsert(root.id, _record(file_path, size=123, md5="f" * 32))

        record = storage.files.get_by_root_and_path(root_id=root.id, path=str(file_path))
        assert record is not None
        assert record.path == str(file_path)
        assert record.size == 123
        assert record.md5 == "f" * 32

        missing = storage.files.get_by_root_and_path(root_id=root.id, path=str(data_root / "missing.txt"))
        assert missing is None
    finally:
        storage.close()


def test_scan_state_stores_current_file(tmp_path: Path) -> None:
    db_path = tmp_path / "catalogic.db"
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        storage.scan_state.set_running(current_root="/mnt", message="run")
        storage.scan_state.set_current_file(current_file="/mnt/video/big.mkv", current_root="/mnt")
        state = storage.scan_state.get()
        assert state["current_file"] == "/mnt/video/big.mkv"
        assert state["current_root"] == "/mnt"

        storage.scan_state.set_finished(state="idle", desired_state="idle", message="done")
        state = storage.scan_state.get()
        assert state["current_file"] is None
    finally:
        storage.close()


def test_app_settings_update_and_reset(tmp_path: Path) -> None:
    db_path = tmp_path / "catalogic.db"
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        initial = storage.app_settings.get()
        assert initial["hash_mode"] in {"auto", "full", "sample"}

        saved = storage.app_settings.update(
            {
                "hash_mode": "sample",
                "hash_sample_threshold_mb": 64,
                "hash_sample_chunk_mb": 8,
                "ffprobe_timeout_sec": 4.5,
                "ffprobe_analyze_duration_us": 500_000,
                "ffprobe_probesize_bytes": 1_000_000,
            }
        )
        assert saved["hash_mode"] == "sample"
        assert int(saved["hash_sample_threshold_mb"]) == 64
        assert int(saved["hash_sample_chunk_mb"]) == 8
        assert float(saved["ffprobe_timeout_sec"]) == 4.5

        reset = storage.app_settings.reset_defaults()
        assert reset["hash_mode"] == "auto"
        assert int(reset["hash_sample_threshold_mb"]) == 256
        assert int(reset["hash_sample_chunk_mb"]) == 4
    finally:
        storage.close()
