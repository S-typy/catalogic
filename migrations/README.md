# Миграции БД

Версионируемые миграции схемы. Добавление новых миграций — см. SPEC.md, раздел 2.3.

## Текущие миграции

- `001_initial.sql`:
  - таблица `scan_roots`;
  - таблица `files` (upsert-ключ `UNIQUE(root_id, path)`);
  - индексы по `path` и `md5`.
- `002_scan_state.sql`:
  - таблица `scan_state` для статуса фонового сканера (`idle/running/stopped/failed`);
  - initial row `id=1`.
- `003_scan_control.sql`:
  - поля `desired_state` и `follow_symlinks` в `scan_state`;
  - backend пишет желаемое состояние, scanner-service исполняет команду.
- `004_worker_heartbeat.sql`:
  - поля `worker_last_seen`, `worker_pid`, `worker_host` в `scan_state`;
  - позволяют API видеть, что отдельный scanner-service жив.
