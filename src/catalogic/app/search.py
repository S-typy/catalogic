"""Use case: поиск по имени (в т.ч. wildcard)."""

from __future__ import annotations

from typing import Any

from catalogic.app.catalog import search_files


def run_search(db_path: str, pattern: str, *, limit: int = 200, offset: int = 0) -> list[dict[str, Any]]:
    return search_files(db_path, pattern, limit=limit, offset=offset)
