"""Точка входа отдельного frontend service."""

from __future__ import annotations

import os
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from catalogic.config import load_settings


def create_frontend_app(api_base: str) -> FastAPI:
    app = FastAPI(title="Catalogic STEP1 Frontend", version="0.1.0")
    web_dir = Path(__file__).resolve().parents[1] / "web"
    static_dir = web_dir / "static"
    app_js = static_dir / "app.js"
    styles_css = static_dir / "styles.css"
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    def index() -> str:
        html = (web_dir / "index.html").read_text(encoding="utf-8")
        version = str(
            int(
                max(
                    app_js.stat().st_mtime if app_js.exists() else 0,
                    styles_css.stat().st_mtime if styles_css.exists() else 0,
                )
            )
        )
        inject = f"<script>window.CATALOGIC_API_BASE = {api_base!r};</script>"
        html = html.replace(
            "<link rel=\"stylesheet\" href=\"/static/styles.css\">",
            f"<link rel=\"stylesheet\" href=\"/static/styles.css?v={version}\">",
        )
        html = html.replace(
            "<script src=\"/static/app.js\"></script>",
            f"{inject}\n  <script src=\"/static/app.js?v={version}\"></script>",
        )
        return html

    return app


def main() -> None:
    settings = load_settings()
    api_base = os.getenv("CATALOGIC_API_BASE", f"http://127.0.0.1:{settings.port}")
    app = create_frontend_app(api_base)
    uvicorn.run(app, host=settings.frontend_host, port=settings.frontend_port)


if __name__ == "__main__":
    main()
