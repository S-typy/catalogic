"""Слой приложения (use cases)."""

from catalogic.app.catalog import (
    add_root,
    build_tree,
    delete_root,
    find_duplicates,
    get_file_details,
    list_roots,
    list_tree_children,
    search_files,
)
from catalogic.app.scan import run_scan
from catalogic.app.scanner_service import ScannerService
from catalogic.app.scanner_worker import ScannerWorker

__all__ = [
    "run_scan",
    "ScannerService",
    "ScannerWorker",
    "list_roots",
    "add_root",
    "delete_root",
    "search_files",
    "build_tree",
    "list_tree_children",
    "get_file_details",
    "find_duplicates",
]
