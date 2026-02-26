"""Точка входа сервер: запуск REST API."""

from __future__ import annotations

import logging

import uvicorn

from catalogic.api import create_app
from catalogic.config import load_settings
from catalogic.logging_setup import configure_logging


def main() -> None:
    settings = load_settings()
    configure_logging(
        service_name="backend",
        level=settings.log_level,
        json_logs=settings.log_json,
        log_file=settings.backend_log_file,
        max_bytes=settings.log_max_bytes,
        backup_count=settings.log_backup_count,
    )
    logger = logging.getLogger("catalogic.server")
    app = create_app(
        db_path=settings.db_path,
        frontend_port=settings.frontend_port,
        browse_root=settings.browse_root,
    )
    logger.info(
        "starting backend host=%s port=%s db=%s",
        settings.host,
        settings.port,
        settings.db_path,
    )
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_config=None,
        access_log=False,
    )


if __name__ == "__main__":
    main()
