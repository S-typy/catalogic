"""Загрузка конфигурации (env-first для STEP1)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    db_path: str
    host: str
    port: int
    frontend_host: str
    frontend_port: int
    browse_root: str


def load_settings() -> Settings:
    db_path = os.getenv("CATALOGIC_DB_PATH", str(Path.cwd() / "data" / "catalogic.db"))
    host = os.getenv("CATALOGIC_HOST", "0.0.0.0")
    port = int(os.getenv("CATALOGIC_PORT", "8080"))
    frontend_host = os.getenv("CATALOGIC_FRONTEND_HOST", "0.0.0.0")
    frontend_port = int(os.getenv("CATALOGIC_FRONTEND_PORT", "8081"))
    browse_root = os.getenv("CATALOGIC_BROWSE_ROOT", "/")
    return Settings(
        db_path=db_path,
        host=host,
        port=port,
        frontend_host=frontend_host,
        frontend_port=frontend_port,
        browse_root=browse_root,
    )
