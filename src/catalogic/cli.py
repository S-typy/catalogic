"""Точка входа CLI: парсинг аргументов, вызов app-сервисов."""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path
from typing import Sequence

from catalogic.app import run_scan
from catalogic.core.exceptions import ScannerError
from catalogic.storage import apply_sqlite_migrations, connect_sqlite, open_sqlite_storage


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="catalogic",
        description="Каталогизатор файлов: сканирование и поиск.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser(
        "scan",
        help="Сканировать директорию и вывести статистику.",
    )
    scan_parser.add_argument(
        "--root",
        required=True,
        help="Корневая директория для сканирования.",
    )
    scan_parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Переходить по символическим ссылкам на директории.",
    )
    scan_parser.add_argument(
        "--db",
        help="Путь к SQLite БД. Если указан, результаты скана сохраняются в БД.",
    )
    scan_parser.set_defaults(handler=_cmd_scan)

    db_parser = subparsers.add_parser(
        "db",
        help="Операции с БД.",
    )
    db_subparsers = db_parser.add_subparsers(dest="db_command", required=True)
    db_migrate_parser = db_subparsers.add_parser(
        "migrate",
        help="Применить миграции к SQLite БД.",
    )
    db_migrate_parser.add_argument(
        "--db",
        required=True,
        help="Путь к SQLite БД.",
    )
    db_migrate_parser.set_defaults(handler=_cmd_db_migrate)
    return parser


def _cmd_scan(args: argparse.Namespace) -> int:
    storage = None
    sink = None
    root_id: int | None = None
    try:
        root_path = Path(args.root).expanduser()
        if not root_path.is_dir():
            raise ScannerError(f"Not a directory: {root_path}")

        if args.db:
            storage = open_sqlite_storage(args.db, migrate=True)
            scan_root = storage.scan_roots.get_or_create(args.root)
            if scan_root.id is None:
                raise RuntimeError("scan root id was not assigned")
            root_id = scan_root.id
            sink = lambda record: storage.files.upsert(root_id, record)

        stats = run_scan(
            args.root,
            follow_symlinks=args.follow_symlinks,
            sink=sink,
        )
    except ScannerError as e:
        print(f"Scan failed: {e}", file=sys.stderr)
        return 2
    except (sqlite3.Error, OSError, RuntimeError) as e:
        print(f"Database error: {e}", file=sys.stderr)
        return 3
    finally:
        if storage is not None:
            storage.close()

    print("Scan completed")
    print(f"Root: {stats.root}")
    print(f"Files discovered: {stats.files_discovered}")
    print(f"Records emitted: {stats.records_emitted}")
    print(f"Skipped files: {stats.skipped_files}")
    print(f"Duration: {stats.duration_sec:.3f} sec")
    if args.db:
        print(f"Stored to DB: {stats.records_emitted}")
        print(f"DB root id: {root_id}")
    return 0


def _cmd_db_migrate(args: argparse.Namespace) -> int:
    conn = None
    try:
        conn = connect_sqlite(args.db)
        applied = apply_sqlite_migrations(conn)
    except (sqlite3.Error, OSError, FileNotFoundError) as e:
        print(f"Migration failed: {e}", file=sys.stderr)
        return 3
    finally:
        if conn is not None:
            conn.close()

    if applied:
        print("Migrations applied:")
        for version in applied:
            print(f"- {version}")
    else:
        print("Migrations are up to date")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Точка входа для команды catalogic."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    handler = args.handler
    return handler(args)
