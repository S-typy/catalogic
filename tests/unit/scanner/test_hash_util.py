"""Тесты стратегий хэширования."""

from __future__ import annotations

import hashlib
from pathlib import Path

from catalogic.scanner.hash_util import SAMPLED_MD5_PREFIX, compute_md5


def test_compute_md5_full_mode(tmp_path: Path, monkeypatch) -> None:
    file_path = tmp_path / "a.bin"
    file_path.write_bytes(b"abc")

    monkeypatch.setenv("CATALOGIC_HASH_MODE", "full")
    result = compute_md5(file_path, size_hint=file_path.stat().st_size)

    assert result == hashlib.md5(b"abc").hexdigest()


def test_compute_md5_auto_mode_uses_sample_for_large_files(tmp_path: Path, monkeypatch) -> None:
    file_path = tmp_path / "video.bin"
    file_path.write_bytes(b"A" * (2 * 1024 * 1024))

    monkeypatch.setenv("CATALOGIC_HASH_MODE", "auto")
    monkeypatch.setenv("CATALOGIC_HASH_SAMPLE_THRESHOLD_MB", "1")
    monkeypatch.setenv("CATALOGIC_HASH_SAMPLE_CHUNK_MB", "1")

    result = compute_md5(file_path, size_hint=file_path.stat().st_size)
    assert result is not None
    assert result.startswith(SAMPLED_MD5_PREFIX)
