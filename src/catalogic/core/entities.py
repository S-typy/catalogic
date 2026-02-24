"""Сущности: File, ScanRoot, Group, …"""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VideoMetadata:
    """Метаданные видео — для отчёта General / Video / Audio."""

    duration_sec: float
    video_codec: str | None
    video_bitrate_bps: int | None
    width: int | None
    height: int | None
    fps: float | None
    audio_codec: str | None
    audio_bitrate_bps: int | None
    audio_channels: int | None
    audio_sample_rate_hz: int | None


@dataclass(frozen=True)
class AudioMetadata:
    """Метаданные аудио — для отчёта Audio."""

    codec: str | None
    bitrate_bps: int | None
    channels: int | None
    sample_rate_hz: int | None


@dataclass(frozen=True)
class ImageMetadata:
    """Метаданные изображения: размер в пикселях, DPI, глубина цвета."""

    width_px: int
    height_px: int
    dpi_x: float | None
    dpi_y: float | None
    color_depth_bits: int | None


@dataclass(frozen=True)
class FileRecord:
    """
    Запись о файле — результат сканирования.
    Обязательно: имя, путь, размер, даты, MIME (magic), MD5.
    По типу файла: video_meta, audio_meta, image_meta.
    """

    path: str
    size: int
    mtime: float
    ctime: float
    mime: str | None
    is_symlink: bool
    md5: str | None
    video_meta: VideoMetadata | None = None
    audio_meta: AudioMetadata | None = None
    image_meta: ImageMetadata | None = None

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("path must be non-empty")
        if self.size < 0:
            raise ValueError("size must be >= 0")

    @property
    def path_obj(self) -> Path:
        return Path(self.path)

    @property
    def name(self) -> str:
        return self.path_obj.name


@dataclass
class ScanRoot:
    """Корень сканирования — путь, который пользователь добавил в скан."""

    id: int | None
    path: str

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("path must be non-empty")
