"""Тесты CLI."""

from pathlib import Path

from catalogic.cli import main
from catalogic.storage import open_sqlite_storage


def test_cli_scan_success(tmp_path: Path, capsys) -> None:
    """Команда scan возвращает 0 и печатает статистику."""
    (tmp_path / "a.txt").write_text("aa")
    code = main(["scan", "--root", str(tmp_path)])
    out = capsys.readouterr().out

    assert code == 0
    assert "Scan completed" in out
    assert "Files discovered: 1" in out
    assert "Records emitted: 1" in out
    assert "Skipped files: 0" in out


def test_cli_scan_not_directory(tmp_path: Path, capsys) -> None:
    """Команда scan на не-директории возвращает ненулевой код и сообщение об ошибке."""
    missing_dir = tmp_path / "missing"
    code = main(["scan", "--root", str(missing_dir)])
    err = capsys.readouterr().err

    assert code == 2
    assert "Scan failed:" in err


def test_cli_db_migrate(tmp_path: Path, capsys) -> None:
    """Команда db migrate создаёт схему БД."""
    db_path = tmp_path / "catalogic.db"
    code = main(["db", "migrate", "--db", str(db_path)])
    out = capsys.readouterr().out

    assert code == 0
    assert ("Migrations applied:" in out) or ("Migrations are up to date" in out)


def test_cli_scan_with_db_persists_records(tmp_path: Path, capsys) -> None:
    """scan --db сохраняет отсканированные файлы в SQLite."""
    data_root = tmp_path / "data"
    data_root.mkdir()
    (data_root / "a.txt").write_text("aa")
    db_path = tmp_path / "catalogic.db"

    code = main(["scan", "--root", str(data_root), "--db", str(db_path)])
    out = capsys.readouterr().out
    assert code == 0
    assert "Stored to DB: 1" in out

    storage = open_sqlite_storage(db_path, migrate=True)
    try:
        results = storage.files.search_by_name("a.txt")
        assert len(results) == 1
        assert results[0].name == "a.txt"
    finally:
        storage.close()
