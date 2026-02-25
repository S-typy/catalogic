"""Вычисление MD5 хэша файла."""

import hashlib
import os
from pathlib import Path
from typing import Any

DEFAULT_CHUNK_SIZE = 4 << 20  # 4 MiB
LARGE_FILE_CHUNK_SIZE = 16 << 20  # 16 MiB
LARGE_FILE_THRESHOLD = 1 << 30  # 1 GiB
DEFAULT_HASH_MODE = "auto"
DEFAULT_SAMPLE_THRESHOLD_MB = 256
DEFAULT_SAMPLE_CHUNK_MB = 4
SAMPLED_MD5_PREFIX = "sample:"


def _pick_chunk_size(size_hint: int | None) -> int:
    if size_hint is not None and size_hint >= LARGE_FILE_THRESHOLD:
        return LARGE_FILE_CHUNK_SIZE
    return DEFAULT_CHUNK_SIZE


def _read_int_env(name: str, default: int, *, minimum: int) -> int:
    raw = os.getenv(name, "").strip()
    return _to_int(raw, default=default, minimum=minimum)


def _to_int(raw: Any, *, default: int, minimum: int) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return value if value >= minimum else default


def _normalize_mode(raw: Any) -> str:
    raw = str(raw or "").strip().lower()
    if raw in {"full", "sample", "auto"}:
        return raw
    return DEFAULT_HASH_MODE


def _hash_mode(scanner_settings: dict[str, Any] | None = None) -> str:
    if scanner_settings is not None and "hash_mode" in scanner_settings:
        return _normalize_mode(scanner_settings.get("hash_mode"))
    return _normalize_mode(os.getenv("CATALOGIC_HASH_MODE", DEFAULT_HASH_MODE))


def _sample_threshold_mb(scanner_settings: dict[str, Any] | None = None) -> int:
    if scanner_settings is not None and "hash_sample_threshold_mb" in scanner_settings:
        return _to_int(
            scanner_settings.get("hash_sample_threshold_mb"),
            default=DEFAULT_SAMPLE_THRESHOLD_MB,
            minimum=0,
        )
    return _read_int_env(
        "CATALOGIC_HASH_SAMPLE_THRESHOLD_MB",
        DEFAULT_SAMPLE_THRESHOLD_MB,
        minimum=0,
    )


def _sample_threshold_bytes(scanner_settings: dict[str, Any] | None = None) -> int:
    mb = _sample_threshold_mb(scanner_settings)
    return mb * 1024 * 1024


def _sample_chunk_mb(scanner_settings: dict[str, Any] | None = None) -> int:
    if scanner_settings is not None and "hash_sample_chunk_mb" in scanner_settings:
        return _to_int(
            scanner_settings.get("hash_sample_chunk_mb"),
            default=DEFAULT_SAMPLE_CHUNK_MB,
            minimum=1,
        )
    return _read_int_env(
        "CATALOGIC_HASH_SAMPLE_CHUNK_MB",
        DEFAULT_SAMPLE_CHUNK_MB,
        minimum=1,
    )


def _sample_chunk_size_bytes(scanner_settings: dict[str, Any] | None = None) -> int:
    mb = _sample_chunk_mb(scanner_settings)
    return mb * 1024 * 1024


def describe_hash_policy(scanner_settings: dict[str, Any] | None = None) -> dict[str, int | str]:
    return {
        "hash_mode": _hash_mode(scanner_settings),
        "sample_threshold_bytes": _sample_threshold_bytes(scanner_settings),
        "sample_chunk_bytes": _sample_chunk_size_bytes(scanner_settings),
        "sample_prefix": SAMPLED_MD5_PREFIX,
    }


def _compute_md5_full(path: Path, *, size_hint: int | None = None) -> str | None:
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


def _compute_md5_sample(
    path: Path,
    *,
    size_hint: int | None = None,
    scanner_settings: dict[str, Any] | None = None,
) -> str | None:
    """
    Быстрый sampled-hash:
    - начало файла
    - середина файла
    - конец файла
    + размер файла
    """
    try:
        size = int(size_hint) if size_hint is not None else int(path.stat().st_size)
    except OSError:
        return None

    chunk_size = _sample_chunk_size_bytes(scanner_settings)
    h = hashlib.md5()
    h.update(b"catalogic-sampled-md5-v1\0")
    h.update(str(size).encode("utf-8", errors="replace"))

    try:
        with open(path, "rb") as f:
            head = f.read(chunk_size)
            h.update(head)

            if size > chunk_size * 2:
                middle_offset = max(0, (size // 2) - (chunk_size // 2))
                f.seek(middle_offset)
                middle = f.read(chunk_size)
                h.update(middle)

            if size > chunk_size:
                tail_offset = max(0, size - chunk_size)
                f.seek(tail_offset)
                tail = f.read(chunk_size)
                h.update(tail)
    except OSError:
        return None

    return f"{SAMPLED_MD5_PREFIX}{h.hexdigest()}"


def compute_md5(
    path: Path | str,
    *,
    size_hint: int | None = None,
    scanner_settings: dict[str, Any] | None = None,
) -> str | None:
    """Вычисляет хэш файла (полный MD5 или sampled-hash). При ошибке чтения возвращает None."""
    path = Path(path)
    if not path.is_file():
        return None

    effective_size = size_hint
    if effective_size is None:
        try:
            effective_size = int(path.stat().st_size)
        except OSError:
            effective_size = None

    mode = _hash_mode(scanner_settings)
    if mode == "full":
        return _compute_md5_full(path, size_hint=effective_size)
    if mode == "sample":
        return _compute_md5_sample(path, size_hint=effective_size, scanner_settings=scanner_settings)

    threshold = _sample_threshold_bytes(scanner_settings)
    if effective_size is not None and effective_size >= threshold:
        return _compute_md5_sample(path, size_hint=effective_size, scanner_settings=scanner_settings)
    return _compute_md5_full(path, size_hint=effective_size)
