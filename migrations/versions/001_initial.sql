CREATE TABLE IF NOT EXISTS scan_roots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    path TEXT NOT NULL UNIQUE,
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    root_id INTEGER NOT NULL,
    path TEXT NOT NULL,
    size INTEGER NOT NULL,
    mtime REAL NOT NULL,
    ctime REAL NOT NULL,
    mime TEXT,
    is_symlink INTEGER NOT NULL,
    md5 TEXT,
    video_meta_json TEXT,
    audio_meta_json TEXT,
    image_meta_json TEXT,
    updated_at REAL NOT NULL,
    FOREIGN KEY (root_id) REFERENCES scan_roots(id) ON DELETE CASCADE,
    UNIQUE (root_id, path)
);

CREATE INDEX IF NOT EXISTS idx_files_name ON files(path);
CREATE INDEX IF NOT EXISTS idx_files_md5 ON files(md5);
