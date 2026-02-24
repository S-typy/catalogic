"""Интеграционные тесты: REST API."""

from __future__ import annotations

import time
from pathlib import Path

from fastapi.testclient import TestClient

from catalogic.app import ScannerWorker
from catalogic.api.app import create_app


def _wait_scan_complete(client: TestClient, timeout_sec: float = 10.0) -> dict:
    deadline = time.time() + timeout_sec
    last_status: dict = {}
    while time.time() < deadline:
        last_status = client.get("/api/scan/status").json()
        if last_status.get("state") in {"idle", "failed", "stopped"} and not last_status.get("is_running"):
            return last_status
        time.sleep(0.1)
    return last_status


def test_api_scan_tree_search_duplicates(tmp_path: Path) -> None:
    data_root = tmp_path / "data"
    (data_root / "a").mkdir(parents=True)
    (data_root / "b").mkdir(parents=True)
    (data_root / "a" / "dup.txt").write_text("ab")
    (data_root / "b" / "dup.txt").write_text("cd")
    (data_root / "a" / "single.md").write_text("hello")

    db_path = tmp_path / "catalogic.db"
    app = create_app(db_path=str(db_path), frontend_port=8081)
    client = TestClient(app)
    worker = ScannerWorker(str(db_path))

    r = client.post("/api/roots", json={"path": str(data_root)})
    assert r.status_code == 201
    root_id = int(r.json()["id"])

    # Without worker heartbeat start should be rejected.
    r = client.post("/api/scan/start", json={})
    assert r.status_code == 503

    # Worker must send heartbeat before backend allows scan start.
    assert worker.run_pending_once() is False

    r = client.post("/api/scan/start", json={})
    assert r.status_code == 200
    assert worker.run_pending_once() is True

    status = _wait_scan_complete(client)
    assert status.get("state") == "idle"
    assert int(status.get("processed_files", 0)) >= 3
    assert status.get("worker_alive") is True

    worker_diag = client.get("/api/scan/worker")
    assert worker_diag.status_code == 200
    assert worker_diag.json()["worker_alive"] is True

    tree = client.get("/api/tree")
    assert tree.status_code == 200
    assert tree.json()["roots"]

    tree_root = client.get("/api/tree/children", params={"root_id": root_id})
    assert tree_root.status_code == 200
    root_children = tree_root.json()["children"]
    root_names = [item["name"] for item in root_children]
    assert root_names == ["a", "b"]

    a_path = next(item["path"] for item in root_children if item["name"] == "a")
    tree_a = client.get("/api/tree/children", params={"root_id": root_id, "dir_path": a_path})
    assert tree_a.status_code == 200
    a_children = tree_a.json()["children"]
    assert [item["name"] for item in a_children] == ["dup.txt", "single.md"]
    assert all(isinstance(item["mtime"], float) for item in a_children)

    search = client.get("/api/search", params={"pattern": "*.txt"})
    assert search.status_code == 200
    assert search.json()["count"] >= 2

    dups = client.get("/api/duplicates")
    assert dups.status_code == 200
    groups = dups.json()["groups"]
    assert groups
    assert groups[0]["name"] == "dup.txt"


def test_api_fs_list_dirs(tmp_path: Path) -> None:
    root = tmp_path / "browse"
    (root / "alpha").mkdir(parents=True)
    (root / "beta").mkdir(parents=True)

    db_path = tmp_path / "catalogic.db"
    app = create_app(db_path=str(db_path), frontend_port=8081, browse_root=str(root))
    client = TestClient(app)

    top = client.get("/api/fs/list-dirs")
    assert top.status_code == 200
    payload = top.json()
    assert payload["current_path"] == str(root.resolve())
    names = [item["name"] for item in payload["dirs"]]
    assert names == ["alpha", "beta"]

    child = client.get("/api/fs/list-dirs", params={"path": str((root / "alpha").resolve())})
    assert child.status_code == 200
    assert child.json()["current_path"] == str((root / "alpha").resolve())
