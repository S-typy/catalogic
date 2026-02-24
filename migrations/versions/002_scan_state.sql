CREATE TABLE IF NOT EXISTS scan_state (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    state TEXT NOT NULL,
    started_at REAL,
    updated_at REAL NOT NULL,
    finished_at REAL,
    processed_files INTEGER NOT NULL DEFAULT 0,
    emitted_records INTEGER NOT NULL DEFAULT 0,
    skipped_files INTEGER NOT NULL DEFAULT 0,
    current_root TEXT,
    message TEXT
);

INSERT OR IGNORE INTO scan_state(
    id,
    state,
    started_at,
    updated_at,
    finished_at,
    processed_files,
    emitted_records,
    skipped_files,
    current_root,
    message
)
VALUES (1, 'idle', NULL, 0, NULL, 0, 0, 0, NULL, NULL);
