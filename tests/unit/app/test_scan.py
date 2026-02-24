"""Тесты use case run_scan()."""

from pathlib import Path

from catalogic.app.scan import run_scan


def test_run_scan_returns_stats_and_sends_records_to_sink(tmp_path: Path) -> None:
    """run_scan прокидывает записи в sink и возвращает агрегированную статистику."""
    (tmp_path / "a.txt").write_text("aa")
    (tmp_path / "b.txt").write_text("bb")
    collected: list[str] = []

    stats = run_scan(
        tmp_path,
        sink=lambda record: collected.append(record.name),
    )

    assert sorted(collected) == ["a.txt", "b.txt"]
    assert stats.records_emitted == 2
    assert stats.files_discovered == 2
    assert stats.skipped_files == 0
    assert stats.finished_at is not None
