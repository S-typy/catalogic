"""Абстрактные репозитории."""

from __future__ import annotations

from abc import ABC, abstractmethod

from catalogic.core.entities import FileRecord, ScanRoot


class ScanRootRepository(ABC):
    """Репозиторий корней сканирования."""

    @abstractmethod
    def get_or_create(self, path: str) -> ScanRoot:
        """Возвращает существующий корень или создаёт новый."""

    @abstractmethod
    def get_by_id(self, root_id: int) -> ScanRoot | None:
        """Возвращает корень по ID."""

    @abstractmethod
    def list_all(self) -> list[ScanRoot]:
        """Возвращает список всех корней."""


class FileRepository(ABC):
    """Репозиторий файлов."""

    @abstractmethod
    def upsert(self, root_id: int, record: FileRecord) -> None:
        """Вставляет или обновляет запись о файле."""

    @abstractmethod
    def search_by_name(
        self,
        query: str,
        *,
        limit: int = 100,
        offset: int = 0,
    ) -> list[FileRecord]:
        """Ищет файлы по подстроке имени."""

    @abstractmethod
    def count_by_root(self, root_id: int) -> int:
        """Количество записей файлов для заданного корня."""
