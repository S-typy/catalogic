"""Запуск scanner-service процесса для STEP1."""

from __future__ import annotations

from catalogic.app import ScannerWorker
from catalogic.config import load_settings


def main() -> None:
    settings = load_settings()
    worker = ScannerWorker(settings.db_path)
    worker.run_forever(poll_interval_sec=1.0)


if __name__ == "__main__":
    main()
