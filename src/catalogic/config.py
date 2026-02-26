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
    log_level: str
    log_json: bool
    backend_log_file: str | None
    log_max_bytes: int
    log_backup_count: int


def _env_str(name: str, default: str) -> str:
    raw = os.getenv(name)
    if raw is None:
        return default
    value = raw.strip()
    return value if value else default


def _env_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def load_settings() -> Settings:
    db_path = _env_str("CATALOGIC_DB_PATH", str(Path.cwd() / "data" / "catalogic.db"))
    host = _env_str("CATALOGIC_HOST", "0.0.0.0")
    port = _env_int("CATALOGIC_PORT", 8080)
    frontend_host = _env_str("CATALOGIC_FRONTEND_HOST", "0.0.0.0")
    frontend_port = _env_int("CATALOGIC_FRONTEND_PORT", 8081)
    browse_root = _env_str("CATALOGIC_BROWSE_ROOT", "/")
    log_level = _env_str("CATALOGIC_LOG_LEVEL", "INFO")
    log_json = _env_bool("CATALOGIC_LOG_JSON", False)
    backend_log_file_raw = os.getenv("CATALOGIC_BACKEND_LOG_FILE")
    backend_log_file = backend_log_file_raw.strip() if backend_log_file_raw is not None else None
    if backend_log_file == "":
        backend_log_file = None
    log_max_bytes = _env_int("CATALOGIC_LOG_MAX_BYTES", 10 * 1024 * 1024)
    log_backup_count = _env_int("CATALOGIC_LOG_BACKUP_COUNT", 5)
    return Settings(
        db_path=db_path,
        host=host,
        port=port,
        frontend_host=frontend_host,
        frontend_port=frontend_port,
        browse_root=browse_root,
        log_level=log_level,
        log_json=log_json,
        backend_log_file=backend_log_file,
        log_max_bytes=log_max_bytes,
        log_backup_count=log_backup_count,
    )
