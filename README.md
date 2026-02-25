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

4. Запуск CLI:

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

4. Run CLI:

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

## Frontend Notes

RU:
- Во вкладке `Настройки` есть `Выбрать каталог` (server-side directory picker).
- Ограничение области выбора задаётся `CATALOGIC_BROWSE_ROOT` в `.env`.
- Добавлен выбор языка интерфейса: `Русский / English`.
- Можно открыть UI с `?lang=ru` или `?lang=en` для принудительного выбора языка.
- При первом запуске (если язык ещё не сохранён) язык определяется по настройкам браузера.

EN:
- `Settings` tab includes `Choose folder` (server-side directory picker).
- Picker scope is limited by `CATALOGIC_BROWSE_ROOT` in `.env`.
- UI language selector is available: `Russian / English`.
- You can force UI language via `?lang=ru` or `?lang=en`.
- On first launch (when no saved language exists), UI language is auto-detected from browser settings.

## Docs

RU/EN: проектная документация находится в `.docs/` (task, spec, structure).
