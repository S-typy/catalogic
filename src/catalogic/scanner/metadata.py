"""Размер, даты, MIME (magic), MD5, медиа-метаданные (видео/аудио/изображение)."""

import os
from pathlib import Path
from typing import Any

from catalogic.core.entities import FileRecord

from catalogic.scanner.hash_util import compute_md5
from catalogic.scanner.image_meta import get_image_metadata
from catalogic.scanner.mime_magic import get_mime
from catalogic.scanner.video_audio_meta import get_audio_metadata, get_video_metadata

# MIME-префиксы для выбора типа извлечения
VIDEO_MIME_PREFIXES = ("video/",)
AUDIO_MIME_PREFIXES = ("audio/",)
IMAGE_MIME_PREFIXES = ("image/",)


def _normalize_path(path: Path | str) -> Path:
    """
    Нормализует путь до абсолютного без разыменования символических ссылок.
    """
    p = Path(path).expanduser()
    if p.is_absolute():
        return p
    return Path(os.path.abspath(p))


def _get_stat_metadata(path: Path) -> tuple[int, float, float, bool] | None:
    """size, mtime, ctime, is_symlink. При ошибке — None."""
    try:
        st = path.stat(follow_symlinks=True)
        return (st.st_size, st.st_mtime, st.st_ctime, path.is_symlink())
    except OSError:
        return None


def get_file_record(
    path: Path | str,
    *,
    scanner_settings: dict[str, Any] | None = None,
) -> FileRecord | None:
    """
    Собирает полную запись о файле:
    имя (из пути), полный путь, размер, дата создания, дата изменения,
    MIME (magic), MD5; для видео/аудио/изображений — соответствующие метаданные.
    При ошибке доступа возвращает None.
    """
    path = _normalize_path(path)
    if not path.is_file():
        return None

    raw = _get_stat_metadata(path)
    if raw is None:
        return None
    size, mtime, ctime, is_symlink = raw

    mime = get_mime(path)
    md5 = compute_md5(path, size_hint=size, scanner_settings=scanner_settings)

    video_meta = None
    audio_meta = None
    image_meta = None

    if mime:
        if mime.startswith(VIDEO_MIME_PREFIXES):
            video_meta = get_video_metadata(path, scanner_settings=scanner_settings)
        elif mime.startswith(AUDIO_MIME_PREFIXES):
            audio_meta = get_audio_metadata(path, scanner_settings=scanner_settings)
        elif mime.startswith(IMAGE_MIME_PREFIXES):
            image_meta = get_image_metadata(path)

    return FileRecord(
        path=str(path),
        size=size,
        mtime=mtime,
        ctime=ctime,
        mime=mime,
        is_symlink=is_symlink,
        md5=md5,
        video_meta=video_meta,
        audio_meta=audio_meta,
        image_meta=image_meta,
    )


def get_file_record_with_cached_md5(
    path: Path | str,
    *,
    cached_size: int | None,
    cached_mtime: float | None,
    cached_md5: str | None,
    scanner_settings: dict[str, Any] | None = None,
) -> FileRecord | None:
    """
    Как get_file_record, но переиспользует ранее вычисленный MD5, если файл не изменился.
    """
    path_obj = _normalize_path(path)
    if not path_obj.is_file():
        return None

    raw = _get_stat_metadata(path_obj)
    if raw is None:
        return None
    size, mtime, ctime, is_symlink = raw

    mime = get_mime(path_obj)
    if cached_md5 and cached_size == size and cached_mtime == mtime:
        md5 = cached_md5
    else:
        md5 = compute_md5(path_obj, size_hint=size, scanner_settings=scanner_settings)

    video_meta = None
    audio_meta = None
    image_meta = None

    if mime:
        if mime.startswith(VIDEO_MIME_PREFIXES):
            video_meta = get_video_metadata(path_obj, scanner_settings=scanner_settings)
        elif mime.startswith(AUDIO_MIME_PREFIXES):
            audio_meta = get_audio_metadata(path_obj, scanner_settings=scanner_settings)
        elif mime.startswith(IMAGE_MIME_PREFIXES):
            image_meta = get_image_metadata(path_obj)

    return FileRecord(
        path=str(path_obj),
        size=size,
        mtime=mtime,
        ctime=ctime,
        mime=mime,
        is_symlink=is_symlink,
        md5=md5,
        video_meta=video_meta,
        audio_meta=audio_meta,
        image_meta=image_meta,
    )
