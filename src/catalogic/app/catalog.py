"""Use cases для работы с каталогом файлов в БД."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any

from catalogic.core.entities import FileRecord, ScanRoot
from catalogic.storage import open_sqlite_storage


def _serialize_record(record: FileRecord) -> dict[str, Any]:
    return {
        "path": record.path,
        "name": record.name,
        "size": record.size,
        "mtime": record.mtime,
        "ctime": record.ctime,
        "mime": record.mime,
        "is_symlink": record.is_symlink,
        "md5": record.md5,
    }


def _serialize_meta(meta: object | None) -> dict[str, Any] | None:
    if meta is None:
        return None
    if is_dataclass(meta):
        return asdict(meta)
    return {"value": str(meta)}


def list_roots(db_path: str) -> list[ScanRoot]:
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        return storage.scan_roots.list_all()
    finally:
        storage.close()


def add_root(db_path: str, path: str) -> ScanRoot:
    normalized = str(Path(path).expanduser())
    if not Path(normalized).is_dir():
        raise ValueError(f"Not a directory: {normalized}")

    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        return storage.scan_roots.get_or_create(normalized)
    finally:
        storage.close()


def delete_root(db_path: str, root_id: int) -> bool:
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        with storage.conn:
            cur = storage.conn.execute("DELETE FROM scan_roots WHERE id = ?", (int(root_id),))
        return cur.rowcount > 0
    finally:
        storage.close()


def search_files(db_path: str, pattern: str, *, limit: int = 200, offset: int = 0) -> list[dict[str, Any]]:
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        records = storage.files.search_by_wildcard(pattern, limit=limit, offset=offset)
        return [_serialize_record(record) for record in records]
    finally:
        storage.close()


def find_duplicates(db_path: str, *, limit_groups: int = 200) -> list[dict[str, Any]]:
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        return storage.files.find_duplicates_by_name_size(limit_groups=limit_groups)
    finally:
        storage.close()


def build_tree(db_path: str, *, root_id: int | None = None) -> list[dict[str, Any]]:
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        roots = storage.scan_roots.list_all()
        root_map = {int(root.id): root for root in roots if root.id is not None}
        rows = storage.files.list_tree_rows(root_id=root_id)
    finally:
        storage.close()

    nodes_by_root: dict[int, dict[str, Any]] = {}
    for rid, _, _ in rows:
        if rid in nodes_by_root:
            continue
        root = root_map.get(rid)
        root_path = root.path if root is not None else f"root-{rid}"
        nodes_by_root[rid] = {
            "name": Path(root_path).name or root_path,
            "path": root_path,
            "type": "dir",
            "children": [],
            "_children_map": {},
        }

    for rid, file_path, size in rows:
        root = root_map.get(rid)
        root_path = Path(root.path) if root is not None else Path("/")
        node = nodes_by_root.setdefault(
            rid,
            {
                "name": f"root-{rid}",
                "path": str(root_path),
                "type": "dir",
                "children": [],
                "_children_map": {},
            },
        )

        try:
            relative_parts = Path(file_path).relative_to(root_path).parts
        except ValueError:
            relative_parts = Path(file_path).parts[-1:]

        if not relative_parts:
            continue

        current = node
        for part in relative_parts[:-1]:
            current_map = current["_children_map"]
            if part not in current_map:
                dir_path = str(Path(current["path"]) / part)
                dir_node = {
                    "name": part,
                    "path": dir_path,
                    "type": "dir",
                    "children": [],
                    "_children_map": {},
                }
                current["children"].append(dir_node)
                current_map[part] = dir_node
            current = current_map[part]

        file_name = relative_parts[-1]
        current["children"].append(
            {
                "name": file_name,
                "path": file_path,
                "type": "file",
                "size": size,
            }
        )

    result: list[dict[str, Any]] = []
    for node in nodes_by_root.values():
        _cleanup_tree(node)
        result.append(node)
    result.sort(key=lambda item: str(item["path"]))
    return result


def list_tree_children(
    db_path: str,
    *,
    root_id: int,
    dir_path: str | None = None,
) -> dict[str, Any]:
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        root = storage.scan_roots.get_by_id(int(root_id))
        if root is None:
            raise ValueError(f"Root not found: {root_id}")

        root_path = str(Path(root.path).expanduser().resolve())
        current_path = str(Path(dir_path).expanduser().resolve()) if dir_path else root_path
        try:
            Path(current_path).relative_to(Path(root_path))
        except ValueError as e:
            raise ValueError("Directory path is outside root") from e

        children = storage.files.list_directory_children(
            root_id=int(root.id),
            root_path=root_path,
            dir_path=current_path,
        )
    finally:
        storage.close()

    return {
        "root_id": int(root.id),
        "root_path": root_path,
        "dir_path": current_path,
        "children": children,
    }


def get_file_details(db_path: str, *, root_id: int, path: str) -> dict[str, Any] | None:
    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        root = storage.scan_roots.get_by_id(int(root_id))
        if root is None:
            return None
        record = storage.files.get_by_root_and_path(root_id=int(root.id), path=path)
    finally:
        storage.close()

    if record is None:
        return None

    payload = _serialize_record(record)
    payload["root_id"] = int(root.id)
    payload["video_meta"] = _serialize_meta(record.video_meta)
    payload["audio_meta"] = _serialize_meta(record.audio_meta)
    payload["image_meta"] = _serialize_meta(record.image_meta)
    return payload


def _cleanup_tree(node: dict[str, Any]) -> None:
    if node.get("type") != "dir":
        return
    children = node.get("children") or []
    for child in children:
        _cleanup_tree(child)
    children.sort(key=lambda item: (item.get("type") != "dir", str(item.get("name"))))
    node.pop("_children_map", None)
