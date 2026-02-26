"""Общая настройка logging для сервисов Catalogic."""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

_REQUEST_ID_CTX: ContextVar[str] = ContextVar("catalogic_request_id", default="-")


def set_request_id(request_id: str) -> Token[str]:
    return _REQUEST_ID_CTX.set(request_id or "-")


def reset_request_id(token: Token[str]) -> None:
    _REQUEST_ID_CTX.reset(token)


def get_request_id() -> str:
    return _REQUEST_ID_CTX.get()


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _resolve_level(level_name: str) -> int:
    value = getattr(logging, str(level_name).strip().upper(), None)
    if isinstance(value, int):
        return value
    return logging.INFO


def _build_formatter(json_logs: bool) -> logging.Formatter:
    if json_logs:
        return JsonFormatter()
    return logging.Formatter(
        fmt="%(asctime)s %(levelname)s [%(name)s] [rid=%(request_id)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _build_handlers(
    *,
    formatter: logging.Formatter,
    log_file: str | None,
    max_bytes: int,
    backup_count: int,
) -> tuple[list[logging.Handler], str | None]:
    request_filter = RequestIdFilter()
    handlers: list[logging.Handler] = []
    file_log_error: str | None = None

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    stream_handler.addFilter(request_filter)
    handlers.append(stream_handler)

    if log_file:
        try:
            log_path = Path(log_file).expanduser()
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                filename=str(log_path),
                maxBytes=max(1, int(max_bytes)),
                backupCount=max(1, int(backup_count)),
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            file_handler.addFilter(request_filter)
            handlers.append(file_handler)
        except OSError as err:
            file_log_error = f"{log_file}: {err}"
            print(
                f"[catalogic] WARNING: cannot enable file logging ({file_log_error}), using stdout only",
                file=sys.stderr,
            )

    return handlers, file_log_error


def configure_logging(
    *,
    service_name: str,
    level: str = "INFO",
    json_logs: bool = False,
    log_file: str | None = None,
    max_bytes: int = 10 * 1024 * 1024,
    backup_count: int = 5,
) -> None:
    level_no = _resolve_level(level)
    formatter = _build_formatter(json_logs)
    handlers, file_log_error = _build_handlers(
        formatter=formatter,
        log_file=log_file,
        max_bytes=max_bytes,
        backup_count=backup_count,
    )

    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
    root.setLevel(level_no)
    for handler in handlers:
        root.addHandler(handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access", "catalogic"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(level_no)
        logger.propagate = True
        for handler in list(logger.handlers):
            logger.removeHandler(handler)

    logging.captureWarnings(True)
    logging.getLogger("catalogic.bootstrap").info(
        "logging configured service=%s level=%s json=%s file=%s",
        service_name,
        logging.getLevelName(level_no),
        bool(json_logs),
        log_file or "-",
    )
    if file_log_error:
        logging.getLogger("catalogic.bootstrap").warning(
            "file logging disabled service=%s reason=%s",
            service_name,
            file_log_error,
        )
