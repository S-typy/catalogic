# Catalogic

## Русский

Умный мультиплатформенный каталогизатор файлов для больших хранилищ (миллионы файлов, десятки и сотни терабайт). Сканирует заданные каталоги, строит единую базу с метаданными и связями между файлами (дубликаты, производные версии, один контент в разных форматах). Поддерживается режим агентов: несколько сканеров могут отправлять данные в центральную БД. Доступ к данным через REST API и CLI; опционально веб-интерфейс. В перспективе — упорядочивание с ИИ: дедупликация, выбор лучшей версии, замена копий ссылками (symlink/hardlink), перекодирование.

Технологии: Python 3.12+, REST API, CLI. Выбор БД при инициализации (напр. SQLite для NAS с 1 ГБ RAM). Развёртывание: локально, Docker, как сервис; под Windows — отдельный сервис-обёртка. Платформы: Linux, Windows, macOS, Synology NAS. Только open source компоненты.

Лицензия: PolyForm Noncommercial 1.0.0. Только некоммерческое использование; при распространении обязательно сохранять указание первоначального автора и источника (Required Notice). Коммерческое использование — по соглашению.

---

## English

A multi-platform file cataloger for large storage systems (millions of files, tens or hundreds of terabytes). Scans given directories, builds a unified database with metadata and relationships between files (duplicates, derivative versions, same content in different formats). Agent mode supported: multiple scanners can send data to a central DB. Access via REST API and CLI; optional web UI. Future: AI-assisted organization (deduplication, best-version selection, replacing copies with symlinks/hardlinks, re-encoding).

Stack: Python 3.12+, REST API, CLI. DB chosen at init (e.g. SQLite for 1 GB RAM NAS). Deployment: local, Docker, as a service; on Windows, a separate service wrapper. Platforms: Linux, Windows, macOS, Synology NAS. Open source components only.

License: PolyForm Noncommercial 1.0.0. Non-commercial use only; distribution must preserve the original author and source (Required Notice). Commercial use by agreement.
