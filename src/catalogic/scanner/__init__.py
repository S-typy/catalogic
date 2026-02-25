"""Обход ФС и извлечение метаданных."""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator

from catalogic.core.entities import FileRecord

from catalogic.scanner.hash_util import compute_md5
from catalogic.scanner.metadata import get_file_record
from catalogic.scanner.mime_magic import get_mime
from catalogic.scanner.walker import iterate_files


@dataclass(slots=True)
class ScanStats:
    """Статистика одного прохода сканера."""

    root: str
    files_discovered: int = 0
    records_emitted: int = 0
    skipped_files: int = 0
    interrupted: bool = False
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None

    @property
    def duration_sec(self) -> float:
        """Длительность скана в секундах."""
        end = self.finished_at if self.finished_at is not None else time.time()
        return max(0.0, end - self.started_at)


def _iter_scan_records(
    root: Path,
    *,
    follow_symlinks: bool,
    stats: ScanStats,
    should_stop: Callable[[], bool] | None = None,
    on_progress: Callable[[ScanStats], None] | None = None,
    on_file_start: Callable[[Path], None] | None = None,
    scanner_settings: dict[str, Any] | None = None,
) -> Iterator[FileRecord]:
    for path in iterate_files(root, follow_symlinks=follow_symlinks):
        if on_file_start is not None:
            on_file_start(path)
        if should_stop is not None and should_stop():
            stats.interrupted = True
            break
        stats.files_discovered += 1
        record = get_file_record(path, scanner_settings=scanner_settings)
        if record is None:
            stats.skipped_files += 1
            if on_progress is not None:
                on_progress(stats)
            continue
        stats.records_emitted += 1
        if on_progress is not None:
            on_progress(stats)
        yield record


def scan(
    root: str | Path,
    *,
    follow_symlinks: bool = False,
) -> Iterator[FileRecord]:
    """
    Сканирует дерево каталогов и отдаёт по одной записи FileRecord для каждого файла.

    Недоступные файлы пропускаются (не отдаются в потоке).
    """
    stats = ScanStats(root=str(Path(root).resolve()))
    try:
        yield from _iter_scan_records(
            Path(root),
            follow_symlinks=follow_symlinks,
            stats=stats,
        )
    finally:
        stats.finished_at = time.time()


def scan_with_stats(
    root: str | Path,
    *,
    follow_symlinks: bool = False,
    on_record: Callable[[FileRecord], None] | None = None,
    should_stop: Callable[[], bool] | None = None,
    on_progress: Callable[[ScanStats], None] | None = None,
    on_file_start: Callable[[Path], None] | None = None,
    scanner_settings: dict[str, Any] | None = None,
) -> ScanStats:
    """
    Полностью выполняет скан и возвращает структурированную статистику.

    on_record — опциональный callback для каждой записи (например, upsert в БД).
    """
    stats = ScanStats(root=str(Path(root).resolve()))
    try:
        for record in _iter_scan_records(
            Path(root),
            follow_symlinks=follow_symlinks,
            stats=stats,
            should_stop=should_stop,
            on_progress=on_progress,
            on_file_start=on_file_start,
            scanner_settings=scanner_settings,
        ):
            if on_record is not None:
                on_record(record)
    finally:
        stats.finished_at = time.time()
    return stats


__all__ = [
    "scan",
    "scan_with_stats",
    "ScanStats",
    "iterate_files",
    "get_file_record",
    "FileRecord",
    "get_mime",
    "compute_md5",
]
