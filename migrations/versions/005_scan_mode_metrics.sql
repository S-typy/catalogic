ALTER TABLE scan_state ADD COLUMN scan_mode TEXT NOT NULL DEFAULT 'add_new';
ALTER TABLE scan_state ADD COLUMN processed_image_files INTEGER NOT NULL DEFAULT 0;
ALTER TABLE scan_state ADD COLUMN processed_video_files INTEGER NOT NULL DEFAULT 0;
ALTER TABLE scan_state ADD COLUMN processed_audio_files INTEGER NOT NULL DEFAULT 0;
ALTER TABLE scan_state ADD COLUMN processed_other_files INTEGER NOT NULL DEFAULT 0;
ALTER TABLE scan_state ADD COLUMN skipped_existing_files INTEGER NOT NULL DEFAULT 0;

UPDATE scan_state
SET scan_mode = CASE
    WHEN scan_mode IS NULL OR scan_mode = '' THEN 'add_new'
    ELSE scan_mode
END
WHERE id = 1;
