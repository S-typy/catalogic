"""Тесты обхода каталогов."""

import os
from pathlib import Path

import pytest

from catalogic.core.exceptions import ScannerError
from catalogic.scanner.walker import iterate_files


def _symlink_or_skip(src: Path, dst: Path) -> None:
    try:
        os.symlink(src, dst)
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"symlink is not available in this environment: {e}")


def test_iterate_files_empty_dir(tmp_path: Path) -> None:
    """Пустая директория — нет файлов."""
    assert list(iterate_files(tmp_path)) == []


def test_iterate_files_flat(tmp_path: Path) -> None:
    """Плоский список файлов."""
    (tmp_path / "a.txt").write_text("a")
    (tmp_path / "b.txt").write_text("b")
    (tmp_path / "c").mkdir()
    (tmp_path / "c" / "d.txt").write_text("d")
    paths = list(iterate_files(tmp_path))
    names = sorted(p.name for p in paths)
    assert names == ["a.txt", "b.txt", "d.txt"]


def test_iterate_files_not_dir(tmp_path: Path) -> None:
    """Передача файла вместо директории — ScannerError."""
    f = tmp_path / "f.txt"
    f.write_text("x")
    with pytest.raises(ScannerError, match="Not a directory"):
        list(iterate_files(f))


def test_iterate_files_resolves_root(tmp_path: Path) -> None:
    """Корень приводится к абсолютному пути."""
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "f.txt").write_text("x")
    paths = list(iterate_files(sub))
    assert len(paths) == 1
    assert paths[0].name == "f.txt"
    assert paths[0].is_absolute()


def test_iterate_files_skips_dir_symlink_by_default(tmp_path: Path) -> None:
    """Ссылки на директории не обходятся, если follow_symlinks=False."""
    real = tmp_path / "real"
    real.mkdir()
    (real / "f.txt").write_text("x")
    _symlink_or_skip(real, tmp_path / "link_to_real")

    paths = list(iterate_files(tmp_path))
    assert len(paths) == 1
    assert paths[0].name == "f.txt"


def test_iterate_files_handles_symlink_loop(tmp_path: Path) -> None:
    """Циклические symlink-структуры не приводят к бесконечному обходу."""
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "f.txt").write_text("x")
    _symlink_or_skip(tmp_path, sub / "loop_to_root")

    paths = list(iterate_files(tmp_path, follow_symlinks=True))
    assert len(paths) == 1
    assert paths[0].name == "f.txt"
