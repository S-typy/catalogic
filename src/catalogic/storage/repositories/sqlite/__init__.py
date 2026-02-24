"""Реализация репозиториев для SQLite."""

from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

from catalogic.core.entities import AudioMetadata, FileRecord, ImageMetadata, ScanRoot, VideoMetadata
from catalogic.storage.repositories.base import FileRepository, ScanRootRepository


def _normalize_path(path: str | Path) -> str:
    return os.path.abspath(Path(path).expanduser())


def _to_json(value: object | None) -> str | None:
    if value is None:
        return None
    if hasattr(value, "__dict__"):
        return json.dumps(value.__dict__, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _escape_like(value: str) -> str:
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _wildcard_to_like(pattern: str) -> str:
    chunks: list[str] = []
    for char in pattern:
        if char == "*":
            chunks.append("%")
        elif char == "?":
            chunks.append("_")
        elif char in ("%", "_", "\\"):
            chunks.append("\\" + char)
        else:
            chunks.append(char)
    return "".join(chunks)


def _load_video_meta(raw: str | None) -> VideoMetadata | None:
    if not raw:
        return None
    data = json.loads(raw)
    return VideoMetadata(
        duration_sec=float(data["duration_sec"]),
        video_codec=data.get("video_codec"),
        video_bitrate_bps=data.get("video_bitrate_bps"),
        width=data.get("width"),
        height=data.get("height"),
        fps=data.get("fps"),
        audio_codec=data.get("audio_codec"),
        audio_bitrate_bps=data.get("audio_bitrate_bps"),
        audio_channels=data.get("audio_channels"),
        audio_sample_rate_hz=data.get("audio_sample_rate_hz"),
    )


def _load_audio_meta(raw: str | None) -> AudioMetadata | None:
    if not raw:
        return None
    data = json.loads(raw)
    return AudioMetadata(
        codec=data.get("codec"),
        bitrate_bps=data.get("bitrate_bps"),
        channels=data.get("channels"),
        sample_rate_hz=data.get("sample_rate_hz"),
    )


def _load_image_meta(raw: str | None) -> ImageMetadata | None:
    if not raw:
        return None
    data = json.loads(raw)
    return ImageMetadata(
        width_px=int(data["width_px"]),
        height_px=int(data["height_px"]),
        dpi_x=data.get("dpi_x"),
        dpi_y=data.get("dpi_y"),
        color_depth_bits=data.get("color_depth_bits"),
    )


def _row_to_file_record(row: sqlite3.Row) -> FileRecord:
    return FileRecord(
        path=row["path"],
        size=row["size"],
        mtime=row["mtime"],
        ctime=row["ctime"],
        mime=row["mime"],
        is_symlink=bool(row["is_symlink"]),
        md5=row["md5"],
        video_meta=_load_video_meta(row["video_meta_json"]),
        audio_meta=_load_audio_meta(row["audio_meta_json"]),
        image_meta=_load_image_meta(row["image_meta_json"]),
    )


class SQLiteScanRootRepository(ScanRootRepository):
    """SQLite-реализация репозитория корней сканирования."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def get_or_create(self, path: str) -> ScanRoot:
        normalized = _normalize_path(path)
        cur = self._conn.execute(
            "SELECT id, path FROM scan_roots WHERE path = ?",
            (normalized,),
        )
        row = cur.fetchone()
        if row is not None:
            return ScanRoot(id=row["id"], path=row["path"])

        with self._conn:
            self._conn.execute(
                "INSERT INTO scan_roots(path, created_at) VALUES (?, ?)",
                (normalized, time.time()),
            )
        cur = self._conn.execute(
            "SELECT id, path FROM scan_roots WHERE path = ?",
            (normalized,),
        )
        row = cur.fetchone()
        if row is None:
            raise RuntimeError("failed to create scan root")
        return ScanRoot(id=row["id"], path=row["path"])

    def get_by_id(self, root_id: int) -> ScanRoot | None:
        cur = self._conn.execute(
            "SELECT id, path FROM scan_roots WHERE id = ?",
            (root_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return ScanRoot(id=row["id"], path=row["path"])

    def list_all(self) -> list[ScanRoot]:
        cur = self._conn.execute("SELECT id, path FROM scan_roots ORDER BY id")
        return [ScanRoot(id=row["id"], path=row["path"]) for row in cur.fetchall()]


class SQLiteFileRepository(FileRepository):
    """SQLite-реализация репозитория файлов."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def upsert(self, root_id: int, record: FileRecord) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT INTO files(
                    root_id, path, size, mtime, ctime, mime, is_symlink, md5,
                    video_meta_json, audio_meta_json, image_meta_json, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(root_id, path) DO UPDATE SET
                    size = excluded.size,
                    mtime = excluded.mtime,
                    ctime = excluded.ctime,
                    mime = excluded.mime,
                    is_symlink = excluded.is_symlink,
                    md5 = excluded.md5,
                    video_meta_json = excluded.video_meta_json,
                    audio_meta_json = excluded.audio_meta_json,
                    image_meta_json = excluded.image_meta_json,
                    updated_at = excluded.updated_at
                """,
                (
                    root_id,
                    record.path,
                    record.size,
                    record.mtime,
                    record.ctime,
                    record.mime,
                    int(record.is_symlink),
                    record.md5,
                    _to_json(record.video_meta),
                    _to_json(record.audio_meta),
                    _to_json(record.image_meta),
                    time.time(),
                ),
            )

    def search_by_name(
        self,
        query: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[FileRecord]:
        pattern = f"%{query}%"
        cur = self._conn.execute(
            """
            SELECT
                path, size, mtime, ctime, mime, is_symlink, md5,
                video_meta_json, audio_meta_json, image_meta_json
            FROM files
            WHERE lower(path) LIKE lower(?)
            ORDER BY path
            LIMIT ? OFFSET ?
            """,
            (pattern, int(limit), int(offset)),
        )
        return [_row_to_file_record(row) for row in cur.fetchall()]

    def search_by_wildcard(
        self,
        pattern: str,
        *,
        limit: int = 200,
        offset: int = 0,
    ) -> list[FileRecord]:
        if not pattern:
            return []
        if "*" in pattern or "?" in pattern:
            sql_pattern = _wildcard_to_like(pattern)
        else:
            sql_pattern = f"%{_escape_like(pattern)}%"

        cur = self._conn.execute(
            """
            SELECT
                path, size, mtime, ctime, mime, is_symlink, md5,
                video_meta_json, audio_meta_json, image_meta_json
            FROM files
            WHERE lower(path) LIKE lower(?) ESCAPE '\\'
            ORDER BY path
            LIMIT ? OFFSET ?
            """,
            (sql_pattern, int(limit), int(offset)),
        )
        return [_row_to_file_record(row) for row in cur.fetchall()]

    def count_by_root(self, root_id: int) -> int:
        cur = self._conn.execute(
            "SELECT COUNT(*) AS cnt FROM files WHERE root_id = ?",
            (root_id,),
        )
        row = cur.fetchone()
        if row is None:
            return 0
        return int(row["cnt"])

    def list_tree_rows(self, root_id: int | None = None) -> list[tuple[int, str, int]]:
        if root_id is None:
            cur = self._conn.execute(
                "SELECT root_id, path, size FROM files ORDER BY root_id, path",
            )
        else:
            cur = self._conn.execute(
                "SELECT root_id, path, size FROM files WHERE root_id = ? ORDER BY path",
                (root_id,),
            )
        return [(int(row["root_id"]), str(row["path"]), int(row["size"])) for row in cur.fetchall()]

    def find_duplicates_by_name_size(self, *, limit_groups: int = 200) -> list[dict[str, Any]]:
        cur = self._conn.execute("SELECT path, size FROM files ORDER BY path")
        groups: dict[tuple[str, int], list[str]] = {}
        for row in cur.fetchall():
            path = str(row["path"])
            size = int(row["size"])
            key = (Path(path).name, size)
            groups.setdefault(key, []).append(path)

        duplicates: list[dict[str, Any]] = []
        for (name, size), paths in groups.items():
            if len(paths) < 2:
                continue
            duplicates.append(
                {
                    "name": name,
                    "size": size,
                    "count": len(paths),
                    "paths": sorted(paths),
                }
            )
        duplicates.sort(key=lambda item: (-int(item["count"]), str(item["name"])))
        return duplicates[:limit_groups]


class SQLiteScanStateRepository:
    """SQLite-репозиторий состояния фонового сканера."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        self.ensure_row()

    def ensure_row(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                INSERT OR IGNORE INTO scan_state(
                    id, state, started_at, updated_at, finished_at,
                    processed_files, emitted_records, skipped_files, current_root, message,
                    desired_state, follow_symlinks, worker_last_seen, worker_pid, worker_host
                )
                VALUES (1, 'idle', NULL, ?, NULL, 0, 0, 0, NULL, NULL, 'idle', 0, NULL, NULL, NULL)
                """,
                (time.time(),),
            )

    def get(self) -> dict[str, Any]:
        row = self._conn.execute(
            """
            SELECT
                state, started_at, updated_at, finished_at,
                processed_files, emitted_records, skipped_files, current_root, message,
                desired_state, follow_symlinks, worker_last_seen, worker_pid, worker_host
            FROM scan_state
            WHERE id = 1
            """
        ).fetchone()
        if row is None:
            self.ensure_row()
            return self.get()
        return {
            "state": row["state"],
            "started_at": row["started_at"],
            "updated_at": row["updated_at"],
            "finished_at": row["finished_at"],
            "processed_files": int(row["processed_files"]),
            "emitted_records": int(row["emitted_records"]),
            "skipped_files": int(row["skipped_files"]),
            "current_root": row["current_root"],
            "message": row["message"],
            "desired_state": row["desired_state"],
            "follow_symlinks": bool(row["follow_symlinks"]),
            "worker_last_seen": row["worker_last_seen"],
            "worker_pid": row["worker_pid"],
            "worker_host": row["worker_host"],
        }

    def touch_worker_heartbeat(self, *, pid: int, host: str) -> None:
        with self._conn:
            self._conn.execute(
                """
                UPDATE scan_state
                SET worker_last_seen = ?, worker_pid = ?, worker_host = ?
                WHERE id = 1
                """,
                (time.time(), int(pid), host),
            )

    def set_desired_state(
        self,
        *,
        desired_state: str,
        follow_symlinks: bool | None = None,
        message: str | None = None,
    ) -> None:
        now = time.time()
        if follow_symlinks is None:
            with self._conn:
                self._conn.execute(
                    """
                    UPDATE scan_state
                    SET desired_state = ?, updated_at = ?, message = ?
                    WHERE id = 1
                    """,
                    (desired_state, now, message),
                )
            return
        with self._conn:
            self._conn.execute(
                """
                UPDATE scan_state
                SET desired_state = ?, follow_symlinks = ?, updated_at = ?, message = ?
                WHERE id = 1
                """,
                (desired_state, int(follow_symlinks), now, message),
            )

    def set_running(self, *, current_root: str | None = None, message: str | None = None) -> None:
        now = time.time()
        with self._conn:
            self._conn.execute(
                """
                UPDATE scan_state
                SET
                    state = 'running',
                    desired_state = 'running',
                    started_at = ?,
                    updated_at = ?,
                    finished_at = NULL,
                    processed_files = 0,
                    emitted_records = 0,
                    skipped_files = 0,
                    current_root = ?,
                    message = ?
                WHERE id = 1
                """,
                (now, now, current_root, message),
            )

    def update_progress(
        self,
        *,
        processed_files: int,
        emitted_records: int,
        skipped_files: int,
        current_root: str | None,
    ) -> None:
        with self._conn:
            self._conn.execute(
                """
                UPDATE scan_state
                SET
                    updated_at = ?,
                    processed_files = ?,
                    emitted_records = ?,
                    skipped_files = ?,
                    current_root = ?
                WHERE id = 1
                """,
                (
                    time.time(),
                    int(processed_files),
                    int(emitted_records),
                    int(skipped_files),
                    current_root,
                ),
            )

    def set_finished(
        self,
        *,
        state: str,
        desired_state: str | None = None,
        message: str | None = None,
    ) -> None:
        now = time.time()
        final_desired = desired_state if desired_state is not None else ("running" if state == "running" else "idle")
        with self._conn:
            self._conn.execute(
                """
                UPDATE scan_state
                SET
                    state = ?,
                    desired_state = ?,
                    updated_at = ?,
                    finished_at = ?,
                    message = ?
                WHERE id = 1
                """,
                (state, final_desired, now, now, message),
            )
