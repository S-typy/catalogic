"""Создание FastAPI приложения."""

from __future__ import annotations

import logging
from pathlib import Path
import time
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from catalogic.app import ScannerService
from catalogic.api.routes import create_api_router
from catalogic.logging_setup import reset_request_id, set_request_id
from catalogic.storage import open_sqlite_storage


def create_app(*, db_path: str, frontend_port: int, browse_root: str = "/") -> FastAPI:
    app = FastAPI(title="Catalogic STEP1 API", version="0.1.0")
    app.state.db_path = db_path
    app.state.frontend_port = frontend_port
    app.state.browse_root = browse_root
    app.state.scanner = ScannerService(db_path)
    logger = logging.getLogger("catalogic.api")
    request_logger = logging.getLogger("catalogic.api.request")

    storage = open_sqlite_storage(db_path, migrate=True)
    storage.close()

    app.include_router(create_api_router())

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid4().hex[:12]
        token = set_request_id(request_id)
        started = time.perf_counter()
        client_ip = request.client.host if request.client else "-"
        query = request.url.query or "-"
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            request_logger.exception(
                "http_request_failed method=%s path=%s query=%s client=%s elapsed_ms=%.1f",
                request.method,
                request.url.path,
                query,
                client_ip,
                elapsed_ms,
            )
            raise
        else:
            response.headers["X-Request-ID"] = request_id
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            if request.url.path in {"/api/scan/status", "/api/scan/worker"} and response.status_code < 500:
                level = logging.DEBUG
            else:
                level = logging.WARNING if response.status_code >= 500 else logging.INFO
            request_logger.log(
                level,
                "http_request method=%s path=%s query=%s status=%s client=%s elapsed_ms=%.1f",
                request.method,
                request.url.path,
                query,
                response.status_code,
                client_ip,
                elapsed_ms,
            )
            return response
        finally:
            reset_request_id(token)

    web_dir = Path(__file__).resolve().parents[1] / "web"
    static_dir = web_dir / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.on_event("startup")
    def on_startup() -> None:
        logger.info("api startup db_path=%s browse_root=%s", db_path, browse_root)

    @app.on_event("shutdown")
    def on_shutdown() -> None:
        logger.info("api shutdown")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(str(web_dir / "index.html"))

    return app
