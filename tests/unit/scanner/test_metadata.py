"""Тесты метаданных."""

import os
from pathlib import Path

import pytest

from catalogic.core.entities import FileRecord
from catalogic.scanner.metadata import get_file_record


def _symlink_or_skip(src: Path, dst: Path) -> None:
    try:
        os.symlink(src, dst)
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"symlink is not available in this environment: {e}")


def test_get_file_record_basic(tmp_path: Path) -> None:
    """Размер, даты, MIME, MD5 для обычного файла."""
    f = tmp_path / "test.txt"
    f.write_text("hello")
    record = get_file_record(f)
    assert record is not None
    assert record.path == str(f.resolve())
    assert record.name == "test.txt"
    assert record.size == 5
    assert record.mtime > 0
    assert record.ctime > 0
    assert record.mime == "text/plain"
    assert record.is_symlink is False
    assert record.md5 is not None and len(record.md5) == 32
    assert record.video_meta is None
    assert record.audio_meta is None
    assert record.image_meta is None


def test_get_file_record_nonexistent(tmp_path: Path) -> None:
    """Несуществующий путь — None."""
    assert get_file_record(tmp_path / "nonexistent") is None


def test_get_file_record_keeps_symlink_path(tmp_path: Path) -> None:
    """Для symlink-файла сохраняется путь ссылки, а не целевого файла."""
    target = tmp_path / "target.txt"
    target.write_text("hello")
    link = tmp_path / "link.txt"
    _symlink_or_skip(target, link)

    record = get_file_record(link)
    assert record is not None
    assert record.path == os.path.abspath(link)
    assert record.is_symlink is True


def test_file_record_name() -> None:
    """FileRecord.name — последняя часть пути."""
    r = FileRecord(
        path="/some/dir/file.txt",
        size=0,
        mtime=0.0,
        ctime=0.0,
        mime=None,
        is_symlink=False,
        md5=None,
    )
    assert r.name == "file.txt"
