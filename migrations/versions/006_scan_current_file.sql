ALTER TABLE scan_state ADD COLUMN current_file TEXT;

UPDATE scan_state
SET current_file = NULL
WHERE id = 1;
