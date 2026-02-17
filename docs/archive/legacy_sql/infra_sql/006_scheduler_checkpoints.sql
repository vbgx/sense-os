BEGIN;

CREATE TABLE IF NOT EXISTS scheduler_checkpoints (
  id SERIAL PRIMARY KEY,
  name VARCHAR(64) NOT NULL,
  vertical_id INTEGER NOT NULL,
  source VARCHAR(64) NOT NULL,
  start_day DATE NOT NULL,
  end_day DATE NOT NULL,
  last_completed_day DATE NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'running',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_scheduler_checkpoint UNIQUE (name, vertical_id, source)
);

CREATE INDEX IF NOT EXISTS ix_scheduler_checkpoints_name ON scheduler_checkpoints(name);
CREATE INDEX IF NOT EXISTS ix_scheduler_checkpoints_vertical ON scheduler_checkpoints(vertical_id);

COMMIT;
