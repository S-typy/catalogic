CREATE TABLE IF NOT EXISTS app_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    hash_mode TEXT NOT NULL DEFAULT 'auto',
    hash_sample_threshold_mb INTEGER NOT NULL DEFAULT 256,
    hash_sample_chunk_mb INTEGER NOT NULL DEFAULT 4,
    ffprobe_timeout_sec REAL NOT NULL DEFAULT 8.0,
    ffprobe_analyze_duration_us INTEGER NOT NULL DEFAULT 2000000,
    ffprobe_probesize_bytes INTEGER NOT NULL DEFAULT 5000000,
    updated_at REAL NOT NULL
);

INSERT OR IGNORE INTO app_settings(
    id,
    hash_mode,
    hash_sample_threshold_mb,
    hash_sample_chunk_mb,
    ffprobe_timeout_sec,
    ffprobe_analyze_duration_us,
    ffprobe_probesize_bytes,
    updated_at
)
VALUES (1, 'auto', 256, 4, 8.0, 2000000, 5000000, strftime('%s', 'now'));
