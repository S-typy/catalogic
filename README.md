# Catalogic

Умный мультиплатформенный каталогизатор файлов для больших хранилищ. См. [ABOUT.md](ABOUT.md).

## Установка

```bash
pip install -e .
```

## Запуск

```bash
catalogic --help
```

### STEP1 сервисы

```bash
catalogic-server
catalogic-scanner
catalogic-frontend
```

`scan/start` через API доступен только если `catalogic-scanner` отправляет heartbeat.

Перед установкой настрой `.env` (можно начать с `.env.example`):

```bash
cp .env.example .env
```

One-command installer (Linux/systemd):

```bash
./scripts/install_step1.sh
```

Документация: каталог `.docs/` (ТЗ, спецификация, структура проекта).
