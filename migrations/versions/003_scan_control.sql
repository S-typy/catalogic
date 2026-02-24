ALTER TABLE scan_state ADD COLUMN desired_state TEXT NOT NULL DEFAULT 'idle';
ALTER TABLE scan_state ADD COLUMN follow_symlinks INTEGER NOT NULL DEFAULT 0;

UPDATE scan_state
SET desired_state = CASE
    WHEN state = 'running' THEN 'running'
    WHEN state = 'stopped' THEN 'stopped'
    ELSE 'idle'
END
WHERE id = 1;
