"""REST-эндпоинты STEP1."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

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
        db_path = request.app.state.db_path
        details = get_file_details(db_path, root_id=root_id, path=path)
        if details is None:
            raise HTTPException(status_code=404, detail="File not found")
        return details

    @router.get("/search")
    def get_search(
        request: Request,
        pattern: str = Query(min_length=1),
        limit: int = Query(default=200, ge=1, le=5000),
        offset: int = Query(default=0, ge=0),
    ) -> dict[str, Any]:
        db_path = request.app.state.db_path
        results = search_files(db_path, pattern, limit=limit, offset=offset)
        return {"items": results, "count": len(results)}

    @router.get("/duplicates")
    def get_duplicates(
        request: Request,
        limit_groups: int = Query(default=200, ge=1, le=1000),
    ) -> dict[str, Any]:
        db_path = request.app.state.db_path
        groups = find_duplicates(db_path, limit_groups=limit_groups)
        return {"groups": groups, "count": len(groups)}

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
        return manager.diagnostics()

    return router
