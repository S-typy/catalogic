"""Создание FastAPI приложения."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from catalogic.app import ScannerService
from catalogic.api.routes import create_api_router
from catalogic.storage import open_sqlite_storage


def create_app(*, db_path: str, frontend_port: int) -> FastAPI:
    app = FastAPI(title="Catalogic STEP1 API", version="0.1.0")
    app.state.db_path = db_path
    app.state.frontend_port = frontend_port
    app.state.scanner = ScannerService(db_path)

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

    web_dir = Path(__file__).resolve().parents[1] / "web"
    static_dir = web_dir / "static"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(str(web_dir / "index.html"))

    return app
