"""REST-эндпоинты STEP1."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from catalogic.app import add_root, build_tree, delete_root, find_duplicates, list_roots, search_files


class RootCreateRequest(BaseModel):
    path: str = Field(min_length=1)


class ScanStartRequest(BaseModel):
    root_ids: list[int] | None = None
    follow_symlinks: bool = False


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
        result = manager.start(selected, follow_symlinks=body.follow_symlinks)
        if not result.started:
            raise HTTPException(status_code=409, detail=result.message)
        return {"started": True, "message": result.message, "roots": selected}

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
        return {
            "db_path": request.app.state.db_path,
            "frontend_url": f"http://{request.url.hostname}:{request.app.state.frontend_port}",
        }

    return router
