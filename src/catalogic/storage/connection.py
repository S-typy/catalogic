"""Подключение к БД, выбор адаптера по конфигу."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from catalogic.storage.migrations import apply_sqlite_migrations
from catalogic.storage.repositories.sqlite import (
    SQLiteAppSettingsRepository,
    SQLiteFileRepository,
    SQLiteScanRootRepository,
    SQLiteScanStateRepository,
)


@dataclass(slots=True)
class SQLiteStorage:
    """Контейнер SQLite-подключения и репозиториев."""

    conn: sqlite3.Connection
    scan_roots: SQLiteScanRootRepository
    files: SQLiteFileRepository
    app_settings: SQLiteAppSettingsRepository
    scan_state: SQLiteScanStateRepository

    def close(self) -> None:
        self.conn.close()


def connect_sqlite(db_path: str | Path) -> sqlite3.Connection:
    """
    Открывает SQLite-подключение.

    Для файлового пути создаёт родительский каталог при необходимости.
    """
    db_path = Path(db_path).expanduser()
    if str(db_path) != ":memory:":
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    return conn


def open_sqlite_storage(
    db_path: str | Path,
    *,
    migrate: bool = True,
    migrations_dir: str | Path | None = None,
) -> SQLiteStorage:
    """Открывает storage-объект на SQLite и при необходимости применяет миграции."""
    conn = connect_sqlite(db_path)
    try:
        if migrate:
            apply_sqlite_migrations(conn, migrations_dir=migrations_dir)
        return SQLiteStorage(
            conn=conn,
            scan_roots=SQLiteScanRootRepository(conn),
            files=SQLiteFileRepository(conn),
            app_settings=SQLiteAppSettingsRepository(conn),
            scan_state=SQLiteScanStateRepository(conn),
        )
    except Exception:
        conn.close()
        raise
