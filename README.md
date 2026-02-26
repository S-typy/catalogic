# Catalogic

RU: Умный каталогизатор файлов для больших хранилищ. Подробнее в [ABOUT.md](ABOUT.md).  
EN: Smart file catalog for large storages. See [ABOUT.md](ABOUT.md).

## Quick Start

### RU

1. Установите Python 3.12+.
2. Создайте `.env`:

```bash
cp .env.example .env
```

3. Установите проект:

```bash
pip install -e .
```

4. Примените миграции:

```bash
catalogic db migrate --db ./data/catalogic.db
```

5. Запуск CLI:

```bash
catalogic --help
```

### EN

1. Install Python 3.12+.
2. Create `.env`:

```bash
cp .env.example .env
```

3. Install project:

```bash
pip install -e .
```

4. Apply migrations:

```bash
catalogic db migrate --db ./data/catalogic.db
```

5. Run CLI:

```bash
catalogic --help
```

## STEP1 Services

```bash
catalogic-server
catalogic-scanner
catalogic-frontend
```

RU: `scan/start` через API доступен только если `catalogic-scanner` отправляет heartbeat.  
EN: `scan/start` API is available only when `catalogic-scanner` sends heartbeat.

## Installer (Linux/systemd)

```bash
./scripts/install_step1.sh
```

RU: инсталлер настраивает systemd unit'ы и проверяет наличие `ffprobe` (для video/audio metadata).  
EN: installer configures systemd units and checks `ffprobe` availability (for video/audio metadata).
RU: инсталлер также запускает `catalogic db migrate --db ...` автоматически.  
EN: installer also runs `catalogic db migrate --db ...` automatically.

## Backend Logging

RU:
- В backend включено структурированное логирование запросов: method/path/status/latency/client и `X-Request-ID`.
- Параметры в `.env`:
  - `CATALOGIC_LOG_LEVEL` (`DEBUG|INFO|WARNING|ERROR`)
  - `CATALOGIC_LOG_JSON` (`0|1`)
  - `CATALOGIC_BACKEND_LOG_FILE` (путь для ротации файла логов, если пусто — только stdout/journald)
  - `CATALOGIC_LOG_MAX_BYTES`, `CATALOGIC_LOG_BACKUP_COUNT`

EN:
- Backend now has structured request logging: method/path/status/latency/client and `X-Request-ID`.
- Configure via `.env`:
  - `CATALOGIC_LOG_LEVEL` (`DEBUG|INFO|WARNING|ERROR`)
  - `CATALOGIC_LOG_JSON` (`0|1`)
  - `CATALOGIC_BACKEND_LOG_FILE` (rotating file path; empty means stdout/journald only)
  - `CATALOGIC_LOG_MAX_BYTES`, `CATALOGIC_LOG_BACKUP_COUNT`

## Frontend Notes

RU:
- Во вкладке `Настройки` есть `Выбрать каталог` (server-side directory picker).
- Ограничение области выбора задаётся `CATALOGIC_BROWSE_ROOT` в `.env`.
- Добавлен выбор языка интерфейса: `Русский / English`.
- В статусе отображается текущий обрабатываемый файл.
- Можно открыть UI с `?lang=ru` или `?lang=en` для принудительного выбора языка.
- При первом запуске (если язык ещё не сохранён) язык определяется по настройкам браузера.

EN:
- `Settings` tab includes `Choose folder` (server-side directory picker).
- Picker scope is limited by `CATALOGIC_BROWSE_ROOT` in `.env`.
- UI language selector is available: `Russian / English`.
- Current file being processed is shown in scanner status.
- You can force UI language via `?lang=ru` or `?lang=en`.
- On first launch (when no saved language exists), UI language is auto-detected from browser settings.

## Performance Tuning

RU:
- Параметры производительности теперь задаются в UI:
  - `Настройки -> Производительность сканера`
- В режимах `auto`/`sample` для крупных файлов сохраняется sampled-hash с префиксом `sample:`.

EN:
- Performance parameters are configured in UI:
  - `Settings -> Scanner Performance`
- In `auto`/`sample` modes large files store sampled hash with `sample:` prefix.

## Docs

RU/EN: проектная документация находится в `.docs/` (task, spec, structure).
