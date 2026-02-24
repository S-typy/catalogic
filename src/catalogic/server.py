"""Точка входа сервер: запуск REST API."""

from __future__ import annotations

import uvicorn

from catalogic.api import create_app
from catalogic.config import load_settings


def main() -> None:
    settings = load_settings()
    app = create_app(db_path=settings.db_path, frontend_port=settings.frontend_port)
    uvicorn.run(app, host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
