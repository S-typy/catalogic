"""Helpers for extracting network/proxy info from incoming requests."""

from __future__ import annotations

from typing import Any

from fastapi import Request


def _first_token(raw: str | None) -> str | None:
    if raw is None:
        return None
    value = raw.strip()
    return value or None


def _split_csv(raw: str | None) -> list[str]:
    if not raw:
        return []
    items: list[str] = []
    for part in raw.split(","):
        value = part.strip()
        if value:
            items.append(value)
    return items


def _parse_forwarded(raw: str | None) -> list[dict[str, str]]:
    if not raw:
        return []
    entries: list[dict[str, str]] = []
    for block in _split_csv(raw):
        item: dict[str, str] = {}
        for part in block.split(";"):
            if "=" not in part:
                continue
            key, value = part.split("=", 1)
            k = key.strip().lower()
            v = value.strip().strip('"')
            if not k or not v:
                continue
            item[k] = v
        if item:
            entries.append(item)
    return entries


def extract_request_network_info(request: Request) -> dict[str, Any]:
    headers = request.headers
    peer_ip = request.client.host if request.client else None
    forwarded = _first_token(headers.get("forwarded"))
    xff = _first_token(headers.get("x-forwarded-for"))
    x_real_ip = _first_token(headers.get("x-real-ip"))
    x_forwarded_by = _first_token(headers.get("x-forwarded-by"))
    via = _first_token(headers.get("via"))

    forwarded_entries = _parse_forwarded(forwarded)
    forwarded_for_chain = [entry.get("for") for entry in forwarded_entries if entry.get("for")]
    forwarded_by_chain = [entry.get("by") for entry in forwarded_entries if entry.get("by")]
    xff_chain = _split_csv(xff)

    original_client_ip = (
        (forwarded_for_chain[0] if forwarded_for_chain else None)
        or (xff_chain[0] if xff_chain else None)
        or x_real_ip
        or peer_ip
    )
    proxy_ip = (
        (forwarded_by_chain[-1] if forwarded_by_chain else None)
        or (xff_chain[-1] if len(xff_chain) > 1 else None)
        or x_forwarded_by
        or peer_ip
    )

    return {
        "original_client_ip": original_client_ip,
        "peer_ip": peer_ip,
        "proxy_ip": proxy_ip,
        "x_forwarded_for": xff,
        "x_real_ip": x_real_ip,
        "x_forwarded_by": x_forwarded_by,
        "forwarded": forwarded,
        "via": via,
        "forwarded_for_chain": forwarded_for_chain,
        "forwarded_by_chain": forwarded_by_chain,
        "xff_chain": xff_chain,
    }

