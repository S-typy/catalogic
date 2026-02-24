"""Доменные исключения."""


class CatalogicError(Exception):
    """Базовое исключение приложения."""

    pass


class ScannerError(CatalogicError):
    """Ошибка при сканировании (путь недоступен, не директория и т.д.)."""

    pass
