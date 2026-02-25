"""Метаданные видео и аудио через ffprobe (ffmpeg)."""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from catalogic.core.entities import AudioMetadata, VideoMetadata

_FFPROBE = "ffprobe"
DEFAULT_FFPROBE_TIMEOUT_SEC = 8.0
DEFAULT_FFPROBE_ANALYZE_DURATION_US = 2_000_000
DEFAULT_FFPROBE_PROBESIZE_BYTES = 5_000_000


def _ffprobe_available() -> bool:
    return shutil.which(_FFPROBE) is not None


def _read_int_env(name: str, default: int, *, minimum: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value >= minimum else default


def _read_float_env(name: str, default: float, *, minimum: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        value = float(raw)
    except ValueError:
        return default
    return value if value >= minimum else default


def _to_int(raw: Any, *, default: int, minimum: int) -> int:
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return default
    return value if value >= minimum else default


def _to_float(raw: Any, *, default: float, minimum: float) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return default
    return value if value >= minimum else default


def _ffprobe_timeout_sec(scanner_settings: dict[str, Any] | None = None) -> float:
    if scanner_settings is not None and "ffprobe_timeout_sec" in scanner_settings:
        return _to_float(
            scanner_settings.get("ffprobe_timeout_sec"),
            default=DEFAULT_FFPROBE_TIMEOUT_SEC,
            minimum=1.0,
        )
    return _read_float_env(
        "CATALOGIC_FFPROBE_TIMEOUT_SEC",
        DEFAULT_FFPROBE_TIMEOUT_SEC,
        minimum=1.0,
    )


def _ffprobe_analyze_duration_us(scanner_settings: dict[str, Any] | None = None) -> int:
    if scanner_settings is not None and "ffprobe_analyze_duration_us" in scanner_settings:
        return _to_int(
            scanner_settings.get("ffprobe_analyze_duration_us"),
            default=DEFAULT_FFPROBE_ANALYZE_DURATION_US,
            minimum=0,
        )
    return _read_int_env(
        "CATALOGIC_FFPROBE_ANALYZE_DURATION_US",
        DEFAULT_FFPROBE_ANALYZE_DURATION_US,
        minimum=0,
    )


def _ffprobe_probesize_bytes(scanner_settings: dict[str, Any] | None = None) -> int:
    if scanner_settings is not None and "ffprobe_probesize_bytes" in scanner_settings:
        return _to_int(
            scanner_settings.get("ffprobe_probesize_bytes"),
            default=DEFAULT_FFPROBE_PROBESIZE_BYTES,
            minimum=32_768,
        )
    return _read_int_env(
        "CATALOGIC_FFPROBE_PROBESIZE_BYTES",
        DEFAULT_FFPROBE_PROBESIZE_BYTES,
        minimum=32_768,
    )


def _run_ffprobe(path: Path, *, scanner_settings: dict[str, Any] | None = None) -> dict | None:
    """Запускает облегчённый ffprobe. При ошибке — None."""
    if not path.is_file():
        return None
    if not _ffprobe_available():
        return None
    timeout_sec = _ffprobe_timeout_sec(scanner_settings)
    analyze_duration_us = _ffprobe_analyze_duration_us(scanner_settings)
    probesize_bytes = _ffprobe_probesize_bytes(scanner_settings)
    try:
        r = subprocess.run(
            [
                _FFPROBE,
                "-v",
                "quiet",
                "-probesize",
                str(probesize_bytes),
                "-analyzeduration",
                str(analyze_duration_us),
                "-show_entries",
                (
                    "format=duration,bit_rate:"
                    "stream=codec_type,codec_name,width,height,bit_rate,r_frame_rate,channels,sample_rate"
                ),
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            timeout=timeout_sec,
            check=False,
        )
        if r.returncode != 0:
            return None
        return json.loads(r.stdout.decode("utf-8", errors="replace"))
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError):
        return None


def _parse_fps(r_frame_rate: str | None) -> float | None:
    """Парсит r_frame_rate вида '60000/1001' или '30' в float."""
    if not r_frame_rate:
        return None
    if "/" in r_frame_rate:
        a, b = r_frame_rate.split("/", 1)
        try:
            return float(a.strip()) / float(b.strip())
        except (ValueError, ZeroDivisionError):
            return None
    try:
        return float(r_frame_rate)
    except ValueError:
        return None


def get_video_metadata(path: Path | str, *, scanner_settings: dict[str, Any] | None = None) -> VideoMetadata | None:
    """Извлекает метаданные видео (в т.ч. аудиодорожку) для отчёта General/Video/Audio."""
    path = Path(path)
    data = _run_ffprobe(path, scanner_settings=scanner_settings)
    if not data:
        return None

    streams = data.get("streams") or []
    format_info = data.get("format") or {}

    duration_sec: float = 0.0
    if "duration" in format_info:
        try:
            duration_sec = float(format_info["duration"])
        except (ValueError, TypeError):
            pass

    total_bitrate: int | None = None
    if "bit_rate" in format_info:
        try:
            total_bitrate = int(format_info["bit_rate"])
        except (ValueError, TypeError):
            pass

    video_codec: str | None = None
    video_bitrate_bps: int | None = total_bitrate
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    audio_codec: str | None = None
    audio_bitrate_bps: int | None = None
    audio_channels: int | None = None
    audio_sample_rate_hz: int | None = None

    for s in streams:
        codec_type = s.get("codec_type")
        if codec_type == "video":
            video_codec = s.get("codec_name")
            if "width" in s:
                try:
                    width = int(s["width"])
                except (ValueError, TypeError):
                    pass
            if "height" in s:
                try:
                    height = int(s["height"])
                except (ValueError, TypeError):
                    pass
            if "bit_rate" in s:
                try:
                    video_bitrate_bps = int(s["bit_rate"])
                except (ValueError, TypeError):
                    pass
            fps = _parse_fps(s.get("r_frame_rate"))
        elif codec_type == "audio":
            audio_codec = s.get("codec_name")
            if "bit_rate" in s:
                try:
                    audio_bitrate_bps = int(s["bit_rate"])
                except (ValueError, TypeError):
                    pass
            if "channels" in s:
                try:
                    audio_channels = int(s["channels"])
                except (ValueError, TypeError):
                    pass
            if "sample_rate" in s:
                try:
                    audio_sample_rate_hz = int(s["sample_rate"])
                except (ValueError, TypeError):
                    pass

    return VideoMetadata(
        duration_sec=duration_sec,
        video_codec=video_codec,
        video_bitrate_bps=video_bitrate_bps,
        width=width,
        height=height,
        fps=fps,
        audio_codec=audio_codec,
        audio_bitrate_bps=audio_bitrate_bps,
        audio_channels=audio_channels,
        audio_sample_rate_hz=audio_sample_rate_hz,
    )


def get_audio_metadata(path: Path | str, *, scanner_settings: dict[str, Any] | None = None) -> AudioMetadata | None:
    """Извлекает метаданные аудио для отчёта Audio."""
    path = Path(path)
    data = _run_ffprobe(path, scanner_settings=scanner_settings)
    if not data:
        return None

    streams = data.get("streams") or []
    format_info = data.get("format") or {}
    bit_rate: int | None = None
    if "bit_rate" in format_info:
        try:
            bit_rate = int(format_info["bit_rate"])
        except (ValueError, TypeError):
            pass

    codec: str | None = None
    channels: int | None = None
    sample_rate_hz: int | None = None
    for s in streams:
        if s.get("codec_type") == "audio":
            codec = s.get("codec_name")
            if "bit_rate" in s:
                try:
                    bit_rate = int(s["bit_rate"])
                except (ValueError, TypeError):
                    pass
            if "channels" in s:
                try:
                    channels = int(s["channels"])
                except (ValueError, TypeError):
                    pass
            if "sample_rate" in s:
                try:
                    sample_rate_hz = int(s["sample_rate"])
                except (ValueError, TypeError):
                    pass
            break

    return AudioMetadata(
        codec=codec,
        bitrate_bps=bit_rate,
        channels=channels,
        sample_rate_hz=sample_rate_hz,
    )
