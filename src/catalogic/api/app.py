"""Создание FastAPI приложения."""

from __future__ import annotations

import logging
from pathlib import Path
import time
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from catalogic.app import ScannerService
from catalogic.api.request_context import extract_request_network_info
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
        network_info = extract_request_network_info(request)
        request.state.network_info = network_info
        client_ip = str(network_info.get("original_client_ip") or "-")
        peer_ip = str(network_info.get("peer_ip") or "-")
        proxy_ip = str(network_info.get("proxy_ip") or "-")
        query = request.url.query or "-"
        path = request.url.path
        is_video_request = path.startswith("/api/file/preview/video") or path.startswith("/api/file/view/video")
        if is_video_request:
            request_logger.info(
                "video_http_in method=%s path=%s query=%s client=%s peer=%s proxy=%s range=%s if_range=%s ua=%s referer=%s sec_fetch_dest=%s accept=%s",
                request.method,
                path,
                query,
                client_ip,
                peer_ip,
                proxy_ip,
                request.headers.get("range") or "-",
                request.headers.get("if-range") or "-",
                request.headers.get("user-agent") or "-",
                request.headers.get("referer") or "-",
                request.headers.get("sec-fetch-dest") or "-",
                request.headers.get("accept") or "-",
            )
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            request_logger.exception(
                "http_request_failed method=%s path=%s query=%s client=%s peer=%s proxy=%s elapsed_ms=%.1f",
                request.method,
                request.url.path,
                query,
                client_ip,
                peer_ip,
                proxy_ip,
                elapsed_ms,
            )
            if is_video_request:
                request_logger.exception(
                    "video_http_failed method=%s path=%s query=%s range=%s",
                    request.method,
                    path,
                    query,
                    request.headers.get("range") or "-",
                )
            raise
        else:
            response.headers["X-Request-ID"] = request_id
            if path == "/" or path.startswith("/static/"):
                response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
                response.headers["Pragma"] = "no-cache"
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            if path in {"/api/scan/status", "/api/scan/worker"} and response.status_code < 500:
                level = logging.DEBUG
            else:
                level = logging.WARNING if response.status_code >= 500 else logging.INFO
            request_logger.log(
                level,
                "http_request method=%s path=%s query=%s status=%s client=%s peer=%s proxy=%s elapsed_ms=%.1f",
                request.method,
                request.url.path,
                query,
                response.status_code,
                client_ip,
                peer_ip,
                proxy_ip,
                elapsed_ms,
            )
            if is_video_request:
                request_logger.info(
                    "video_http_out method=%s path=%s status=%s elapsed_ms=%.1f content_type=%s content_length=%s content_range=%s accept_ranges=%s source=%s",
                    request.method,
                    path,
                    response.status_code,
                    elapsed_ms,
                    response.headers.get("content-type") or "-",
                    response.headers.get("content-length") or "-",
                    response.headers.get("content-range") or "-",
                    response.headers.get("accept-ranges") or "-",
                    response.headers.get("x-catalogic-video-source") or "-",
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

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index() -> str:
        app_js = static_dir / "app.js"
        styles_css = static_dir / "styles.css"
        version = str(
            int(
                max(
                    app_js.stat().st_mtime if app_js.exists() else 0,
                    styles_css.stat().st_mtime if styles_css.exists() else 0,
                )
            )
        )
        html = (web_dir / "index.html").read_text(encoding="utf-8")
        html = html.replace(
            "<link rel=\"stylesheet\" href=\"/static/styles.css\">",
            f"<link rel=\"stylesheet\" href=\"/static/styles.css?v={version}\">",
        )
        html = html.replace(
            "<script src=\"/static/app.js\"></script>",
            f"<script src=\"/static/app.js?v={version}\"></script>",
        )
        return html

    return app
