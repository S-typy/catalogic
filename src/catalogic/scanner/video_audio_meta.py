"""Метаданные видео и аудио через ffprobe (ffmpeg)."""

import json
import shutil
import subprocess
from pathlib import Path

from catalogic.core.entities import AudioMetadata, VideoMetadata

_FFPROBE = "ffprobe"


def _ffprobe_available() -> bool:
    return shutil.which(_FFPROBE) is not None


def _run_ffprobe(path: Path) -> dict | None:
    """Запускает ffprobe -show_format -show_streams -of json. При ошибке — None."""
    if not path.is_file():
        return None
    if not _ffprobe_available():
        return None
    try:
        r = subprocess.run(
            [
                _FFPROBE,
                "-v",
                "quiet",
                "-show_format",
                "-show_streams",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            timeout=30,
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


def get_video_metadata(path: Path | str) -> VideoMetadata | None:
    """Извлекает метаданные видео (в т.ч. аудиодорожку) для отчёта General/Video/Audio."""
    path = Path(path)
    data = _run_ffprobe(path)
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


def get_audio_metadata(path: Path | str) -> AudioMetadata | None:
    """Извлекает метаданные аудио для отчёта Audio."""
    path = Path(path)
    data = _run_ffprobe(path)
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
