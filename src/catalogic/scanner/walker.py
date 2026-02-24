"""Обход дерева каталогов."""

import os
from pathlib import Path
from typing import Iterator

from catalogic.core.exceptions import ScannerError


def iterate_files(
    root: Path | str,
    *,
    follow_symlinks: bool = False,
) -> Iterator[Path]:
    """
    Рекурсивно обходит дерево каталогов и отдаёт путь каждого файла (не директории).

    Символические ссылки на файлы отдаются как файлы. Ссылки на директории
    не переходятся, если follow_symlinks=False (по умолчанию).
    Ошибки доступа к отдельным файлам/директориям не прерывают обход —
    такие элементы пропускаются.
    """
    root = Path(root).resolve()
    if not root.is_dir():
        raise ScannerError(f"Not a directory: {root}")

    stack: list[Path] = [root]
    visited_dirs: set[tuple[int, int]] = set()

    while stack:
        current = stack.pop()
        try:
            current_stat = current.stat(follow_symlinks=True)
            current_key = (current_stat.st_dev, current_stat.st_ino)
        except OSError as e:
            if current == root:
                raise ScannerError(f"Cannot access directory {root}: {e}") from e
            continue

        if current_key in visited_dirs:
            continue
        visited_dirs.add(current_key)

        regular_dirs: list[Path] = []
        symlink_dirs: list[Path] = []
        try:
            with os.scandir(current) as it:
                for entry in it:
                    try:
                        if entry.is_dir(follow_symlinks=False):
                            if entry.is_symlink():
                                if follow_symlinks:
                                    symlink_dirs.append(Path(entry.path))
                                continue
                            regular_dirs.append(Path(entry.path))
                            continue

                        if entry.is_file(follow_symlinks=follow_symlinks):
                            yield Path(entry.path)
                    except OSError:
                        continue
        except OSError as e:
            if current == root:
                raise ScannerError(f"Cannot read directory {root}: {e}") from e
            continue

        # LIFO-стек: добавляем symlink-директории раньше, чтобы regular обходились первыми.
        stack.extend(symlink_dirs)
        stack.extend(regular_dirs)
