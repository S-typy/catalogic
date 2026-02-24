ALTER TABLE scan_state ADD COLUMN worker_last_seen REAL;
ALTER TABLE scan_state ADD COLUMN worker_pid INTEGER;
ALTER TABLE scan_state ADD COLUMN worker_host TEXT;
