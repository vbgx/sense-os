-- Sense OS — Patch: ensure pain_instances.vertical_id exists + FK + index (idempotent)
BEGIN;

DO $$
BEGIN
  -- 1) Ensure column exists
  IF NOT EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema='public'
      AND table_name='pain_instances'
      AND column_name='vertical_id'
  ) THEN
    ALTER TABLE pain_instances ADD COLUMN vertical_id INTEGER;
  END IF;

  -- 2) Backfill from signals when possible
  -- (works even if already filled; cheap + safe)
  UPDATE pain_instances pi
  SET vertical_id = s.vertical_id
  FROM signals s
  WHERE pi.signal_id = s.id
    AND (pi.vertical_id IS NULL OR pi.vertical_id <> s.vertical_id);

  -- 3) Ensure FK exists
  IF NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conname = 'fk_pain_instances_vertical_id'
  ) THEN
    ALTER TABLE pain_instances
      ADD CONSTRAINT fk_pain_instances_vertical_id
      FOREIGN KEY (vertical_id)
      REFERENCES verticals(id)
      ON DELETE CASCADE;
  END IF;

  -- 4) Enforce NOT NULL if safe
  IF EXISTS (
    SELECT 1
    FROM information_schema.columns
    WHERE table_schema='public'
      AND table_name='pain_instances'
      AND column_name='vertical_id'
      AND is_nullable = 'YES'
  ) AND NOT EXISTS (
    SELECT 1 FROM pain_instances WHERE vertical_id IS NULL
  ) THEN
    ALTER TABLE pain_instances ALTER COLUMN vertical_id SET NOT NULL;
  END IF;
END $$;

-- 5) Ensure index exists
CREATE INDEX IF NOT EXISTS ix_pain_instances_vertical_id ON pain_instances(vertical_id);

COMMIT;
