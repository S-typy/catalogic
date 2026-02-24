"""Интерфейсы и реализации репозиториев."""

from catalogic.storage.repositories.base import FileRepository, ScanRootRepository
from catalogic.storage.repositories.sqlite import (
    SQLiteFileRepository,
    SQLiteScanRootRepository,
    SQLiteScanStateRepository,
)

__all__ = [
    "FileRepository",
    "ScanRootRepository",
    "SQLiteFileRepository",
    "SQLiteScanRootRepository",
    "SQLiteScanStateRepository",
]
