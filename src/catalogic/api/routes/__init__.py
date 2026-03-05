"""REST-эндпоинты STEP1."""

from __future__ import annotations

from io import BytesIO
from dataclasses import asdict
import logging
import mimetypes
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import tempfile
from threading import BoundedSemaphore, Lock
import time
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, Field
from PIL import Image, ImageOps

from catalogic.app import (
    add_root,
    build_tree,
    delete_root,
    find_duplicates,
    get_file_details,
    list_roots,
    list_tree_children,
    search_files,
)
from catalogic.api.request_context import extract_request_network_info

logger = logging.getLogger("catalogic.api")


class RootCreateRequest(BaseModel):
    path: str = Field(min_length=1)


class ScanStartRequest(BaseModel):
    root_ids: list[int] | None = None
    follow_symlinks: bool = False
    scan_mode: Literal["rebuild", "add_new"] = "add_new"


class ScannerSettingsRequest(BaseModel):
    hash_mode: Literal["auto", "full", "sample"] | None = None
    hash_sample_threshold_mb: int | None = Field(default=None, ge=0)
    hash_sample_chunk_mb: int | None = Field(default=None, ge=1)
    ffprobe_timeout_sec: float | None = Field(default=None, ge=1.0)
    ffprobe_analyze_duration_us: int | None = Field(default=None, ge=0)
    ffprobe_probesize_bytes: int | None = Field(default=None, ge=32768)
    reset_defaults: bool = False


def create_api_router() -> APIRouter:
    router = APIRouter(prefix="/api")
    def _clamp_int(raw: str | None, default: int, *, minimum: int, maximum: int) -> int:
        try:
            value = int(str(raw if raw is not None else default))
        except (TypeError, ValueError):
            value = default
        return max(minimum, min(maximum, value))

    preview_max_procs = _clamp_int(
        os.getenv("CATALOGIC_PREVIEW_MAX_PROCS"),
        2,
        minimum=1,
        maximum=32,
    )
    preview_ffmpeg_threads = _clamp_int(
        os.getenv("CATALOGIC_PREVIEW_FFMPEG_THREADS"),
        1,
        minimum=1,
        maximum=16,
    )
    def _clamp_float(raw: str | None, default: float, *, minimum: float, maximum: float) -> float:
        try:
            value = float(str(raw if raw is not None else default))
        except (TypeError, ValueError):
            value = default
        return max(minimum, min(maximum, value))

    preview_segment_sec = _clamp_float(
        os.getenv("CATALOGIC_PREVIEW_SEGMENT_SEC"),
        12.0,
        minimum=5.0,
        maximum=900.0,
    )
    preview_transcode_timeout_sec = _clamp_float(
        os.getenv("CATALOGIC_PREVIEW_TRANSCODE_TIMEOUT_SEC"),
        120.0,
        minimum=5.0,
        maximum=1800.0,
    )
    preview_slot_wait_sec = _clamp_float(
        os.getenv("CATALOGIC_PREVIEW_SLOT_WAIT_SEC"),
        20.0,
        minimum=0.0,
        maximum=300.0,
    )
    preview_cache_ttl_sec = _clamp_float(
        os.getenv("CATALOGIC_PREVIEW_CACHE_TTL_SEC"),
        120.0,
        minimum=5.0,
        maximum=3600.0,
    )
    preview_cache_max_items = _clamp_int(
        os.getenv("CATALOGIC_PREVIEW_CACHE_MAX_ITEMS"),
        32,
        minimum=2,
        maximum=512,
    )
    video_debug_logs = str(os.getenv("CATALOGIC_VIDEO_DEBUG", "0")).strip().lower() in {"1", "true", "yes", "on"}
    preview_slots = BoundedSemaphore(preview_max_procs)
    preview_active = 0
    preview_lock = Lock()
    preview_cache: dict[str, dict[str, Any]] = {}
    preview_cache_lock = Lock()

    def _cleanup_temp_file(path: str) -> None:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            pass

    def _preview_cache_key(
        *,
        root_id: int,
        path: str,
        container_format: str,
        start_sec: float,
        segment_sec: float,
        width: int,
        video_bitrate_kbps: int,
        audio_bitrate_kbps: int,
    ) -> str:
        return (
            f"{int(root_id)}|{path}|{str(container_format)}|{float(start_sec):.3f}|{float(segment_sec):.3f}|"
            f"{int(width)}|{int(video_bitrate_kbps)}|{int(audio_bitrate_kbps)}"
        )

    def _cleanup_preview_cache() -> None:
        now = time.time()
        to_remove: list[tuple[str, str]] = []
        with preview_cache_lock:
            for key, entry in list(preview_cache.items()):
                cache_path = str(entry.get("path") or "")
                expires_at = float(entry.get("expires_at") or 0.0)
                if not cache_path:
                    to_remove.append((key, cache_path))
                    continue
                if expires_at <= now or not Path(cache_path).exists():
                    to_remove.append((key, cache_path))
            for key, cache_path in to_remove:
                preview_cache.pop(key, None)
                if cache_path:
                    _cleanup_temp_file(cache_path)
            if len(preview_cache) > preview_cache_max_items:
                overflow = len(preview_cache) - preview_cache_max_items
                sorted_keys = sorted(
                    preview_cache.keys(),
                    key=lambda k: float(preview_cache[k].get("expires_at") or 0.0),
                )
                for key in sorted_keys[:overflow]:
                    cache_path = str(preview_cache[key].get("path") or "")
                    preview_cache.pop(key, None)
                    if cache_path:
                        _cleanup_temp_file(cache_path)

    def _resolve_inside_root(raw_path: str | None, browse_root: str) -> tuple[Path, Path]:
        root = Path(browse_root).expanduser().resolve()
        if raw_path:
            candidate = Path(raw_path).expanduser().resolve()
        else:
            candidate = root
        try:
            candidate.relative_to(root)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="Path is outside browse root") from e
        return root, candidate

    def _resolve_scanned_file(request: Request, *, root_id: int, path: str) -> tuple[Path, str]:
        from catalogic.storage import open_sqlite_storage

        storage = open_sqlite_storage(request.app.state.db_path, migrate=True)
        try:
            root = storage.scan_roots.get_by_id(int(root_id))
            record = storage.files.get_by_root_and_path(root_id=int(root_id), path=path)
        finally:
            storage.close()

        if root is None:
            raise HTTPException(status_code=404, detail="Root not found")
        if record is None:
            raise HTTPException(status_code=404, detail="File not found")

        root_path = Path(root.path).expanduser().resolve()
        file_path = Path(record.path).expanduser().resolve()
        try:
            file_path.relative_to(root_path)
        except ValueError as e:
            raise HTTPException(status_code=400, detail="File path is outside root") from e

        if not file_path.is_file():
            raise HTTPException(status_code=404, detail="File does not exist on disk")
        if not os.access(file_path, os.R_OK):
            raise HTTPException(status_code=403, detail="File is not readable by backend service user")

        return file_path, str(record.mime or "")

    def _is_likely_video(path: Path, mime: str) -> bool:
        if mime.lower().startswith("video/"):
            return True
        return path.suffix.lower() in {
            ".mp4",
            ".mkv",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
            ".m4v",
            ".ts",
            ".m2ts",
            ".mpeg",
            ".mpg",
        }

    def _is_likely_image(path: Path, mime: str) -> bool:
        if mime.lower().startswith("image/"):
            return True
        return path.suffix.lower() in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif",
            ".bmp",
            ".tif",
            ".tiff",
            ".avif",
            ".heic",
            ".heif",
        }

    def _resolve_media_type(path: Path, mime: str, expected_prefix: str) -> str:
        lowered = str(mime or "").lower()
        if lowered.startswith(expected_prefix):
            return lowered
        guessed, _ = mimetypes.guess_type(path.name)
        if guessed and guessed.lower().startswith(expected_prefix):
            return guessed.lower()
        return "application/octet-stream"

    @router.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @router.get("/roots")
    def get_roots(request: Request) -> list[dict[str, Any]]:
        db_path = request.app.state.db_path
        return [asdict(root) for root in list_roots(db_path)]

    @router.post("/roots", status_code=201)
    def post_root(body: RootCreateRequest, request: Request) -> dict[str, Any]:
        db_path = request.app.state.db_path
        try:
            root = add_root(db_path, body.path)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return asdict(root)

    @router.delete("/roots/{root_id}")
    def remove_root(root_id: int, request: Request) -> dict[str, Any]:
        db_path = request.app.state.db_path
        deleted = delete_root(db_path, root_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Root not found")
        return {"deleted": True, "root_id": root_id}

    @router.post("/scan/start")
    def start_scan(body: ScanStartRequest, request: Request) -> dict[str, Any]:
        db_path = request.app.state.db_path
        if body.root_ids:
            raise HTTPException(status_code=400, detail="root_ids is not supported in STEP1")
        manager = request.app.state.scanner
        status = manager.status()
        if not status.get("worker_alive"):
            raise HTTPException(status_code=503, detail="Scanner worker is offline")
        roots = list_roots(db_path)
        selected = [root.path for root in roots]
        result = manager.start(
            selected,
            follow_symlinks=body.follow_symlinks,
            scan_mode=body.scan_mode,
        )
        if not result.started:
            raise HTTPException(status_code=409, detail=result.message)
        return {
            "started": True,
            "message": result.message,
            "roots": selected,
            "scan_mode": body.scan_mode,
            "follow_symlinks": body.follow_symlinks,
        }

    @router.post("/scan/stop")
    def stop_scan(request: Request) -> dict[str, Any]:
        manager = request.app.state.scanner
        result = manager.stop()
        if not result.started:
            raise HTTPException(status_code=409, detail=result.message)
        return {"stopped": True, "message": result.message}

    @router.get("/scan/status")
    def scan_status(request: Request) -> dict[str, Any]:
        manager = request.app.state.scanner
        return manager.status()

    @router.get("/scan/worker")
    def scan_worker(request: Request) -> dict[str, Any]:
        manager = request.app.state.scanner
        status = manager.status()
        return {
            "worker_alive": status.get("worker_alive"),
            "worker_stale_sec": status.get("worker_stale_sec"),
            "worker_last_seen": status.get("worker_last_seen"),
            "worker_pid": status.get("worker_pid"),
            "worker_host": status.get("worker_host"),
        }

    @router.get("/fs/list-dirs")
    def fs_list_dirs(
        request: Request,
        path: str | None = Query(default=None),
    ) -> dict[str, Any]:
        browse_root = str(request.app.state.browse_root)
        root, current = _resolve_inside_root(path, browse_root)
        if not current.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")

        dirs: list[dict[str, str]] = []
        try:
            for entry in current.iterdir():
                if entry.is_dir():
                    dirs.append({"name": entry.name, "path": str(entry.resolve())})
        except OSError as e:
            raise HTTPException(status_code=400, detail=f"Cannot list directory: {e}") from e
        dirs.sort(key=lambda item: item["name"].lower())

        parent_path: str | None
        if current == root:
            parent_path = None
        else:
            parent = current.parent.resolve()
            parent.relative_to(root)
            parent_path = str(parent)

        return {
            "browse_root": str(root),
            "current_path": str(current),
            "parent_path": parent_path,
            "dirs": dirs,
        }

    @router.get("/tree")
    def get_tree(
        request: Request,
        root_id: int | None = Query(default=None),
    ) -> dict[str, Any]:
        db_path = request.app.state.db_path
        return {"roots": build_tree(db_path, root_id=root_id)}

    @router.get("/tree/children")
    def get_tree_children(
        request: Request,
        root_id: int = Query(ge=1),
        dir_path: str | None = Query(default=None),
    ) -> dict[str, Any]:
        db_path = request.app.state.db_path
        try:
            return list_tree_children(db_path, root_id=root_id, dir_path=dir_path)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

    @router.get("/file/details")
    def get_file_detail(
        request: Request,
        root_id: int = Query(ge=1),
        path: str = Query(min_length=1),
    ) -> dict[str, Any]:
        started = time.perf_counter()
        logger.info("file.details request root_id=%s path=%s", root_id, path)
        db_path = request.app.state.db_path
        details = get_file_details(db_path, root_id=root_id, path=path)
        if details is None:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            logger.warning("file.details not_found root_id=%s path=%s elapsed_ms=%.1f", root_id, path, elapsed_ms)
            raise HTTPException(status_code=404, detail="File not found")
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        logger.info(
            "file.details ok root_id=%s path=%s elapsed_ms=%.1f size=%s mime=%s",
            root_id,
            path,
            elapsed_ms,
            details.get("size"),
            details.get("mime"),
        )
        return details

    @router.get("/file/preview/image")
    def get_file_image_preview(
        request: Request,
        root_id: int = Query(ge=1),
        path: str = Query(min_length=1),
        width: int = Query(default=420, ge=80, le=1920),
        height: int = Query(default=280, ge=80, le=1080),
        quality: int = Query(default=45, ge=20, le=90),
    ) -> Response:
        file_path, mime = _resolve_scanned_file(request, root_id=root_id, path=path)
        if not mime.lower().startswith("image/"):
            raise HTTPException(status_code=415, detail="Image preview is supported only for image files")

        try:
            with Image.open(file_path) as source:
                image = ImageOps.exif_transpose(source).copy()
        except OSError as e:
            raise HTTPException(status_code=415, detail=f"Cannot decode image: {e}") from e

        image.thumbnail((int(width), int(height)), Image.Resampling.LANCZOS)
        if image.mode in ("RGBA", "LA"):
            alpha = image.getchannel("A")
            base = Image.new("RGB", image.size, (24, 24, 24))
            base.paste(image, mask=alpha)
            image = base
        elif image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        buf = BytesIO()
        image.save(buf, format="WEBP", quality=int(quality), method=4)
        return Response(
            content=buf.getvalue(),
            media_type="image/webp",
            headers={"Cache-Control": "no-store"},
        )

    @router.get("/file/view/image")
    def get_file_image_view(
        request: Request,
        root_id: int = Query(ge=1),
        path: str = Query(min_length=1),
    ) -> FileResponse:
        file_path, mime = _resolve_scanned_file(request, root_id=root_id, path=path)
        if not _is_likely_image(file_path, mime):
            raise HTTPException(status_code=415, detail="Image viewer is supported only for image files")
        media_type = _resolve_media_type(file_path, mime, "image/")
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=file_path.name,
            content_disposition_type="inline",
            headers={"Cache-Control": "no-store"},
        )

    @router.get("/file/view/video")
    def get_file_video_view(
        request: Request,
        root_id: int = Query(ge=1),
        path: str = Query(min_length=1),
    ) -> FileResponse:
        started = time.perf_counter()
        file_path, mime = _resolve_scanned_file(request, root_id=root_id, path=path)
        if not _is_likely_video(file_path, mime):
            raise HTTPException(status_code=415, detail="Video viewer is supported only for video files")
        media_type = _resolve_media_type(file_path, mime, "video/")
        try:
            source_size = file_path.stat().st_size
        except OSError:
            source_size = None
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        logger.info(
            "file.view.video ok root_id=%s path=%s media_type=%s source_size=%s elapsed_ms=%.1f range=%s ua=%s",
            root_id,
            path,
            media_type,
            source_size,
            elapsed_ms,
            request.headers.get("range") or "-",
            request.headers.get("user-agent") or "-",
        )
        return FileResponse(
            path=str(file_path),
            media_type=media_type,
            filename=file_path.name,
            content_disposition_type="inline",
            headers={
                "Cache-Control": "no-store",
                "X-Catalogic-Video-Source": "native-file",
            },
        )

    @router.get("/file/preview/video")
    def get_file_video_preview(
        request: Request,
        root_id: int = Query(ge=1),
        path: str = Query(min_length=1),
        start_sec: float = Query(default=0.0, ge=0.0),
        segment_sec: float | None = Query(default=None, ge=1.0, le=900.0),
        width: int = Query(default=640, ge=160, le=1920),
        video_bitrate_kbps: int = Query(default=700, ge=180, le=4000),
        audio_bitrate_kbps: int = Query(default=96, ge=48, le=256),
        container_format: Literal["mp4", "webm", "ogg"] = Query(default="mp4", alias="format"),
    ) -> FileResponse:
        nonlocal preview_active
        started = time.perf_counter()
        file_path, mime = _resolve_scanned_file(request, root_id=root_id, path=path)
        if not _is_likely_video(file_path, mime):
            raise HTTPException(status_code=415, detail="Video preview is supported only for video files")
        try:
            source_stat = file_path.stat()
            source_size = source_stat.st_size
            source_mtime = source_stat.st_mtime
        except OSError:
            source_size = None
            source_mtime = None

        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise HTTPException(status_code=503, detail="ffmpeg is not available")

        _cleanup_preview_cache()

        segment_value = float(segment_sec) if segment_sec is not None else float(preview_segment_sec)
        segment_value = max(1.0, min(segment_value, float(preview_segment_sec)))
        cache_key = _preview_cache_key(
            root_id=root_id,
            path=path,
            container_format=container_format,
            start_sec=float(start_sec),
            segment_sec=segment_value,
            width=int(width),
            video_bitrate_kbps=int(video_bitrate_kbps),
            audio_bitrate_kbps=int(audio_bitrate_kbps),
        )
        with preview_cache_lock:
            cached = preview_cache.get(cache_key)
            if cached:
                cache_path = str(cached.get("path") or "")
                if cache_path and Path(cache_path).exists():
                    cached["expires_at"] = time.time() + float(preview_cache_ttl_sec)
                    try:
                        cache_size = Path(cache_path).stat().st_size
                    except OSError:
                        cache_size = None
                    logger.info(
                        "file.preview.video cache_hit root_id=%s path=%s format=%s start_sec=%.3f segment_sec=%.1f width=%s cache_path=%s cache_size=%s range=%s ua=%s",
                        root_id,
                        path,
                        container_format,
                        float(start_sec),
                        segment_value,
                        width,
                        cache_path,
                        cache_size,
                        request.headers.get("range") or "-",
                        request.headers.get("user-agent") or "-",
                    )
                    media_type = (
                        "video/webm" if container_format == "webm" else ("video/ogg" if container_format == "ogg" else "video/mp4")
                    )
                    return FileResponse(
                        path=cache_path,
                        media_type=media_type,
                        filename=f"{file_path.stem}_preview.{container_format}",
                        content_disposition_type="inline",
                        headers={
                            "Cache-Control": "no-store",
                            "Accept-Ranges": "bytes",
                            "X-Catalogic-Video-Source": f"preview-cache-hit:{container_format}",
                        },
                    )

        slot_wait_started = time.perf_counter()
        acquired = preview_slots.acquire(timeout=float(preview_slot_wait_sec))
        slot_wait_ms = (time.perf_counter() - slot_wait_started) * 1000.0
        if not acquired:
            logger.warning(
                "file.preview.video slot_timeout root_id=%s path=%s waited_ms=%.1f active=%s limit=%s",
                root_id,
                path,
                slot_wait_ms,
                preview_active,
                preview_max_procs,
            )
            raise HTTPException(
                status_code=429,
                detail=f"Video preview queue timeout (limit={preview_max_procs}, wait_sec={preview_slot_wait_sec})",
                headers={"Retry-After": "2"},
            )
        with preview_lock:
            preview_active += 1
            active_now = preview_active

        ffmpeg_cmd: list[str] = [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-nostdin",
            "-threads",
            str(preview_ffmpeg_threads),
            "-ss",
            f"{float(start_sec):.3f}",
            "-t",
            f"{segment_value:.3f}",
            "-i",
            str(file_path),
            "-map",
            "0:v:0?",
            "-map",
            "0:a:0?",
            "-vf",
            f"scale='min({int(width)},iw)':'-2':flags=lanczos",
            "-r",
            "24",
        ]
        if container_format == "webm":
            ffmpeg_cmd.extend(
                [
                    "-c:v",
                    "libvpx",
                    "-deadline",
                    "realtime",
                    "-cpu-used",
                    "5",
                    "-crf",
                    "34",
                    "-b:v",
                    f"{int(video_bitrate_kbps)}k",
                    "-maxrate",
                    f"{int(video_bitrate_kbps)}k",
                    "-bufsize",
                    f"{int(video_bitrate_kbps) * 2}k",
                    "-g",
                    "96",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "libopus",
                    "-b:a",
                    f"{int(audio_bitrate_kbps)}k",
                    "-ac",
                    "2",
                    "-ar",
                    "48000",
                    "-f",
                    "webm",
                ]
            )
        elif container_format == "ogg":
            ffmpeg_cmd.extend(
                [
                    "-c:v",
                    "libtheora",
                    "-q:v",
                    "5",
                    "-g",
                    "48",
                    "-pix_fmt",
                    "yuv420p",
                    "-c:a",
                    "libvorbis",
                    "-q:a",
                    "4",
                    "-ac",
                    "2",
                    "-ar",
                    "44100",
                    "-f",
                    "ogg",
                ]
            )
        else:
            ffmpeg_cmd.extend(
                [
                    "-c:v",
                    "libx264",
                    "-preset",
                    "veryfast",
                    "-crf",
                    "33",
                    "-pix_fmt",
                    "yuv420p",
                    "-profile:v",
                    "main",
                    "-maxrate",
                    f"{int(video_bitrate_kbps)}k",
                    "-bufsize",
                    f"{int(video_bitrate_kbps) * 2}k",
                    "-g",
                    "48",
                    "-c:a",
                    "aac",
                    "-b:a",
                    f"{int(audio_bitrate_kbps)}k",
                    "-ac",
                    "2",
                    "-ar",
                    "44100",
                    "-movflags",
                    "+faststart",
                    "-f",
                    "mp4",
                ]
            )
        logger.info(
            "file.preview.video start root_id=%s path=%s format=%s source_size=%s source_mtime=%s start_sec=%.3f segment_sec=%.1f width=%s v_bitrate=%sk a_bitrate=%sk ffmpeg=%s threads=%s active=%s limit=%s slot_wait_ms=%.1f range=%s if_range=%s ua=%s",
            root_id,
            path,
            container_format,
            source_size,
            source_mtime,
            float(start_sec),
            segment_value,
            width,
            video_bitrate_kbps,
            audio_bitrate_kbps,
            ffmpeg,
            preview_ffmpeg_threads,
            active_now,
            preview_max_procs,
            slot_wait_ms,
            request.headers.get("range") or "-",
            request.headers.get("if-range") or "-",
            request.headers.get("user-agent") or "-",
        )
        if video_debug_logs:
            logger.info("file.preview.video ffmpeg_cmd=%s", " ".join(shlex.quote(part) for part in ffmpeg_cmd))

        tmp_path: str | None = None
        try:
            fd, raw_tmp_path = tempfile.mkstemp(prefix="catalogic_preview_", suffix=f".{container_format}")
            os.close(fd)
            tmp_path = raw_tmp_path
            ffmpeg_cmd.append(tmp_path)
            completed = subprocess.run(
                ffmpeg_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
                timeout=float(preview_transcode_timeout_sec),
            )
        except subprocess.TimeoutExpired:
            with preview_lock:
                preview_active = max(0, preview_active - 1)
            preview_slots.release()
            if tmp_path:
                _cleanup_temp_file(tmp_path)
            raise HTTPException(status_code=504, detail="Video preview transcode timeout")
        except OSError as e:
            with preview_lock:
                preview_active = max(0, preview_active - 1)
            preview_slots.release()
            if tmp_path:
                _cleanup_temp_file(tmp_path)
            raise HTTPException(status_code=500, detail=f"Cannot start ffmpeg: {e}") from e

        if completed.returncode != 0 or tmp_path is None or not Path(tmp_path).exists() or Path(tmp_path).stat().st_size <= 0:
            if tmp_path:
                _cleanup_temp_file(tmp_path)
            with preview_lock:
                preview_active = max(0, preview_active - 1)
            preview_slots.release()
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            logger.warning(
                "file.preview.video failed root_id=%s path=%s rc=%s elapsed_ms=%.1f stderr=%s",
                root_id,
                path,
                completed.returncode,
                elapsed_ms,
                (completed.stderr or "").strip()[:1000],
            )
            raise HTTPException(status_code=500, detail="Cannot transcode video preview")

        out_size = Path(tmp_path).stat().st_size
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        probe_summary = "-"
        if video_debug_logs:
            ffprobe = shutil.which("ffprobe")
            if ffprobe:
                probe_cmd = [
                    ffprobe,
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration,size:stream=index,codec_type,codec_name,width,height,avg_frame_rate",
                    "-of",
                    "default=noprint_wrappers=1:nokey=0",
                    tmp_path,
                ]
                try:
                    probe_run = subprocess.run(
                        probe_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=5.0,
                    )
                    if probe_run.returncode == 0:
                        probe_summary = " ".join((probe_run.stdout or "").strip().split())[:1400] or "-"
                    else:
                        probe_summary = f"ffprobe_rc={probe_run.returncode} stderr={((probe_run.stderr or '').strip()[:300] or '-')}"
                except Exception as e:
                    probe_summary = f"ffprobe_error={e}"
        logger.info(
            "file.preview.video done root_id=%s path=%s format=%s rc=%s out_path=%s out_bytes=%s elapsed_ms=%.1f probe=%s",
            root_id,
            path,
            container_format,
            completed.returncode,
            tmp_path,
            out_size,
            elapsed_ms,
            probe_summary,
        )
        with preview_lock:
            preview_active = max(0, preview_active - 1)
        preview_slots.release()
        with preview_cache_lock:
            previous = preview_cache.pop(cache_key, None)
            if previous:
                previous_path = str(previous.get("path") or "")
                if previous_path and previous_path != tmp_path:
                    _cleanup_temp_file(previous_path)
            preview_cache[cache_key] = {
                "path": tmp_path,
                "expires_at": time.time() + float(preview_cache_ttl_sec),
            }
        _cleanup_preview_cache()
        media_type = (
            "video/webm" if container_format == "webm" else ("video/ogg" if container_format == "ogg" else "video/mp4")
        )
        return FileResponse(
            path=tmp_path,
            media_type=media_type,
            filename=f"{file_path.stem}_preview.{container_format}",
            content_disposition_type="inline",
            headers={
                "Cache-Control": "no-store",
                "Accept-Ranges": "bytes",
                "X-Catalogic-Video-Source": f"preview-transcoded:{container_format}",
            },
        )

    @router.get("/file/preview/video/check")
    def check_file_video_preview(
        request: Request,
        root_id: int = Query(ge=1),
        path: str = Query(min_length=1),
    ) -> dict[str, Any]:
        file_path, mime = _resolve_scanned_file(request, root_id=root_id, path=path)
        if not _is_likely_video(file_path, mime):
            raise HTTPException(status_code=415, detail="Video preview is supported only for video files")
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise HTTPException(status_code=503, detail="ffmpeg is not available")
        logger.info(
            "file.preview.video.check ok root_id=%s path=%s ffmpeg=%s range=%s ua=%s",
            root_id,
            path,
            ffmpeg,
            request.headers.get("range") or "-",
            request.headers.get("user-agent") or "-",
        )
        return {"ok": True, "ffmpeg": ffmpeg}

    @router.get("/search")
    def get_search(
        request: Request,
        pattern: str = Query(min_length=1),
        limit: int = Query(default=200, ge=1, le=5000),
        offset: int = Query(default=0, ge=0),
    ) -> dict[str, Any]:
        started = time.perf_counter()
        logger.info("search request pattern=%r limit=%s offset=%s", pattern, limit, offset)
        db_path = request.app.state.db_path
        results = search_files(db_path, pattern, limit=limit, offset=offset)
        elapsed_ms = (time.perf_counter() - started) * 1000.0
        logger.info("search ok pattern=%r count=%s elapsed_ms=%.1f", pattern, len(results), elapsed_ms)
        return {"items": results, "count": len(results)}

    @router.get("/duplicates")
    def get_duplicates(
        request: Request,
        mode: Literal["name_size", "md5"] = Query(default="name_size"),
        limit_groups: int = Query(default=200, ge=1, le=1000),
        min_size_bytes: int = Query(default=1, ge=0),
    ) -> dict[str, Any]:
        db_path = request.app.state.db_path
        groups = find_duplicates(
            db_path,
            mode=mode,
            limit_groups=limit_groups,
            min_size_bytes=min_size_bytes,
        )
        total_wasted_bytes = sum(max(0, int(item.get("wasted_size", 0))) for item in groups)
        return {
            "mode": mode,
            "min_size_bytes": int(min_size_bytes),
            "groups": groups,
            "count": len(groups),
            "total_wasted_bytes": total_wasted_bytes,
        }

    @router.get("/settings")
    def get_settings(request: Request) -> dict[str, Any]:
        from catalogic.storage import open_sqlite_storage

        storage = open_sqlite_storage(request.app.state.db_path, migrate=True)
        try:
            scanner_settings = storage.app_settings.get()
        finally:
            storage.close()
        return {
            "db_path": request.app.state.db_path,
            "frontend_url": f"http://{request.url.hostname}:{request.app.state.frontend_port}",
            "browse_root": str(request.app.state.browse_root),
            "scanner": scanner_settings,
        }

    @router.post("/settings")
    def post_settings(body: ScannerSettingsRequest, request: Request) -> dict[str, Any]:
        from catalogic.storage import open_sqlite_storage

        payload = body.model_dump()
        reset_defaults = bool(payload.pop("reset_defaults", False))
        values = {key: value for key, value in payload.items() if value is not None}
        storage = open_sqlite_storage(request.app.state.db_path, migrate=True)
        try:
            if reset_defaults:
                scanner_settings = storage.app_settings.reset_defaults()
            else:
                scanner_settings = storage.app_settings.update(values)
        finally:
            storage.close()
        return {"saved": True, "scanner": scanner_settings}

    @router.get("/state")
    def get_state(request: Request) -> dict[str, Any]:
        manager = request.app.state.scanner
        request_network = getattr(request.state, "network_info", None)
        if not isinstance(request_network, dict):
            request_network = extract_request_network_info(request)
        return {
            **manager.diagnostics(),
            "request_network": request_network,
        }

    return router
