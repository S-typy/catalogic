"""Use case: запуск скана, сохранение записей."""

from pathlib import Path
from typing import Any, Callable

from catalogic.core.entities import FileRecord
from catalogic.scanner import ScanStats, scan_with_stats

RecordSink = Callable[[FileRecord], None]
StopPredicate = Callable[[], bool]
ProgressCallback = Callable[[ScanStats], None]
FileStartCallback = Callable[[Path], None]


def run_scan(
    root: str | Path,
    *,
    follow_symlinks: bool = False,
    sink: RecordSink | None = None,
    should_stop: StopPredicate | None = None,
    on_progress: ProgressCallback | None = None,
    on_file_start: FileStartCallback | None = None,
    scanner_settings: dict[str, Any] | None = None,
) -> ScanStats:
    """
    Выполняет полный проход сканера.

    Если передан sink, каждая запись передаётся в sink (например, для записи в БД).
    Возвращает статистику, пригодную для отображения статуса в CLI/API.
    """
    return scan_with_stats(
        root,
        follow_symlinks=follow_symlinks,
        on_record=sink,
        should_stop=should_stop,
        on_progress=on_progress,
        on_file_start=on_file_start,
        scanner_settings=scanner_settings,
    )
