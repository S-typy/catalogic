"""Тесты точки входа scan()."""

from pathlib import Path

from catalogic.core.entities import FileRecord
from catalogic.scanner import scan, scan_with_stats


def test_scan_yields_records(tmp_path: Path) -> None:
    """scan() отдаёт FileRecord для каждого файла."""
    (tmp_path / "a.txt").write_text("aa")
    (tmp_path / "b.txt").write_text("bb")
    records = list(scan(tmp_path))
    assert len(records) == 2
    names = sorted(r.name for r in records)
    assert names == ["a.txt", "b.txt"]
    for r in records:
        assert isinstance(r, FileRecord)
        assert r.size == 2
        assert r.mime == "text/plain"
        assert r.md5 is not None


def test_scan_with_stats_counts_and_sink(tmp_path: Path) -> None:
    """scan_with_stats возвращает корректные счётчики и вызывает sink."""
    (tmp_path / "a.txt").write_text("aa")
    (tmp_path / "b.txt").write_text("bb")
    seen_names: list[str] = []

    stats = scan_with_stats(
        tmp_path,
        on_record=lambda r: seen_names.append(r.name),
    )

    assert sorted(seen_names) == ["a.txt", "b.txt"]
    assert stats.files_discovered == 2
    assert stats.records_emitted == 2
    assert stats.skipped_files == 0
    assert stats.finished_at is not None
    assert stats.duration_sec >= 0.0
