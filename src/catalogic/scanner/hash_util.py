"""Вычисление MD5 хэша файла."""

import hashlib
from pathlib import Path

CHUNK_SIZE = 1 << 20  # 1 MiB


def compute_md5(path: Path | str) -> str | None:
    """Вычисляет MD5 файла по пути. При ошибке чтения возвращает None."""
    path = Path(path)
    if not path.is_file():
        return None
    h = hashlib.md5()
    try:
        with open(path, "rb") as f:
            while chunk := f.read(CHUNK_SIZE):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None
