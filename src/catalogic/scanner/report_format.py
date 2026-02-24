"""Форматирование метаданных в текстовый отчёт (General / Video / Audio для видео и т.д.)."""

from catalogic.core.entities import AudioMetadata, ImageMetadata, VideoMetadata


def format_duration(seconds: float) -> str:
    """Форматирует длительность в виде '1 h 27 min' или '4 min 30 s'."""
    if seconds <= 0:
        return "0 s"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    parts = []
    if h:
        parts.append(f"{h} h")
    if m:
        parts.append(f"{m} min")
    if s or not parts:
        parts.append(f"{s} s")
    return " ".join(parts)


def format_size_gib(size_bytes: int) -> str:
    """Форматирует размер в GiB (например '4.38 GiB')."""
    return f"{size_bytes / (1024**3):.2f} GiB"


def format_video_report(size_bytes: int, meta: VideoMetadata) -> list[str]:
    """
    Формирует строки отчёта для видео:
    General: 4.38 GiB, 1 h 27 min
    Video: AVC, 7 103 kb/s, 1 920 pixels, 1 080 pixels, 59.940 FPS
    Audio: AAC, 96.0 kb/s, 2 channels, 48.0 kHz
    """
    lines = []
    general_parts = [format_size_gib(size_bytes), format_duration(meta.duration_sec)]
    lines.append("General: " + ", ".join(general_parts))

    video_parts = []
    if meta.video_codec:
        video_parts.append(meta.video_codec.upper())
    if meta.video_bitrate_bps is not None:
        video_parts.append(f"{meta.video_bitrate_bps / 1000:,.0f} kb/s".replace(",", " "))
    if meta.width is not None:
        video_parts.append(f"{meta.width} pixels")
    if meta.height is not None:
        video_parts.append(f"{meta.height} pixels")
    if meta.fps is not None:
        video_parts.append(f"{meta.fps:.3f} FPS")
    if video_parts:
        lines.append("Video: " + ", ".join(video_parts))

    audio_parts = []
    if meta.audio_codec:
        audio_parts.append(meta.audio_codec.upper())
    if meta.audio_bitrate_bps is not None:
        audio_parts.append(f"{meta.audio_bitrate_bps / 1000:.1f} kb/s")
    if meta.audio_channels is not None:
        audio_parts.append(f"{meta.audio_channels} channels")
    if meta.audio_sample_rate_hz is not None:
        audio_parts.append(f"{meta.audio_sample_rate_hz / 1000:.1f} kHz")
    if audio_parts:
        lines.append("Audio: " + ", ".join(audio_parts))

    return lines


def format_audio_report(meta: AudioMetadata) -> str:
    """Одна строка: Audio: AAC, 96.0 kb/s, 2 channels, 48.0 kHz"""
    parts = []
    if meta.codec:
        parts.append(meta.codec.upper())
    if meta.bitrate_bps is not None:
        parts.append(f"{meta.bitrate_bps / 1000:.1f} kb/s")
    if meta.channels is not None:
        parts.append(f"{meta.channels} channels")
    if meta.sample_rate_hz is not None:
        parts.append(f"{meta.sample_rate_hz / 1000:.1f} kHz")
    return "Audio: " + ", ".join(parts) if parts else "Audio: (no metadata)"


def format_image_report(meta: ImageMetadata) -> list[str]:
    """Строки отчёта: размер в пикселях, DPI, глубина цвета."""
    lines = [f"Image: {meta.width_px} x {meta.height_px} pixels"]
    if meta.dpi_x is not None or meta.dpi_y is not None:
        dpi = f"DPI: {meta.dpi_x or 0} x {meta.dpi_y or 0}"
        lines.append(dpi)
    if meta.color_depth_bits is not None:
        lines.append(f"Color depth: {meta.color_depth_bits} bits")
    return lines
