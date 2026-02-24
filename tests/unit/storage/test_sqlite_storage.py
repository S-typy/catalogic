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
