"""Вычисление MD5 хэша файла."""

import hashlib
from pathlib import Path

DEFAULT_CHUNK_SIZE = 4 << 20  # 4 MiB
LARGE_FILE_CHUNK_SIZE = 16 << 20  # 16 MiB
LARGE_FILE_THRESHOLD = 1 << 30  # 1 GiB


def _pick_chunk_size(size_hint: int | None) -> int:
    if size_hint is not None and size_hint >= LARGE_FILE_THRESHOLD:
        return LARGE_FILE_CHUNK_SIZE
    return DEFAULT_CHUNK_SIZE


def compute_md5(path: Path | str, *, size_hint: int | None = None) -> str | None:
    """Вычисляет MD5 файла по пути. При ошибке чтения возвращает None."""
    path = Path(path)
    if not path.is_file():
        return None
    h = hashlib.md5()
    chunk_size = _pick_chunk_size(size_hint)
    buffer = bytearray(chunk_size)
    view = memoryview(buffer)
    try:
        with open(path, "rb") as f:
            while True:
                n = f.readinto(buffer)
                if n <= 0:
                    break
                h.update(view[:n])
        return h.hexdigest()
    except OSError:
        return None
