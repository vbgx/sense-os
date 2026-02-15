BEGIN;

ALTER TABLE pain_instances
  ADD COLUMN IF NOT EXISTS vertical_id INTEGER;

ALTER TABLE pain_instances
  ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT now();

UPDATE pain_instances pi
SET vertical_id = s.vertical_id
FROM signals s
WHERE pi.vertical_id IS NULL
  AND s.id = pi.signal_id;

ALTER TABLE pain_instances
  ALTER COLUMN vertical_id SET NOT NULL;

COMMIT;
