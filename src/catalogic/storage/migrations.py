"""Применение SQL-миграций."""

from __future__ import annotations

import sqlite3
import time
from pathlib import Path


def find_migrations_dir() -> Path:
    """Ищет каталог migrations/versions относительно текущего файла."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "migrations" / "versions"
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("Cannot find migrations/versions directory")


def _ensure_schema_migrations_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations(
            version TEXT PRIMARY KEY,
            applied_at REAL NOT NULL
        )
        """
    )
    conn.commit()


def apply_sqlite_migrations(
    conn: sqlite3.Connection,
    *,
    migrations_dir: str | Path | None = None,
) -> list[str]:
    """Применяет неприменённые миграции SQLite и возвращает список применённых версий."""
    _ensure_schema_migrations_table(conn)

    directory = Path(migrations_dir) if migrations_dir is not None else find_migrations_dir()
    if not directory.exists():
        raise FileNotFoundError(f"Migrations directory not found: {directory}")

    migration_files = sorted(p for p in directory.glob("*.sql") if p.is_file())
    applied_rows = conn.execute("SELECT version FROM schema_migrations").fetchall()
    applied = {row[0] for row in applied_rows}
    newly_applied: list[str] = []

    for migration in migration_files:
        version = migration.name
        if version in applied:
            continue

        script = migration.read_text(encoding="utf-8")
        with conn:
            conn.executescript(script)
            conn.execute(
                "INSERT INTO schema_migrations(version, applied_at) VALUES (?, ?)",
                (version, time.time()),
            )
        newly_applied.append(version)

    return newly_applied
