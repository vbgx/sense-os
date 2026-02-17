-- Idempotency guarantee for processing worker:
-- a given (algo_version, breakdown_hash) must not create duplicates.

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'pain_instances'
          AND column_name = 'breakdown_hash'
    ) THEN
        ALTER TABLE pain_instances
        ADD COLUMN breakdown_hash VARCHAR(32);
    END IF;
END $$;

-- Backfill for existing rows (stable for jsonb)
UPDATE pain_instances
SET breakdown_hash = md5(breakdown::text)
WHERE breakdown_hash IS NULL OR breakdown_hash = '';

ALTER TABLE pain_instances
ALTER COLUMN breakdown_hash SET NOT NULL;

-- Drop legacy idempotency index/constraint if present
ALTER TABLE pain_instances
DROP CONSTRAINT IF EXISTS uq_pain_instances_signal_algo;

DROP INDEX IF EXISTS ux_pain_instances_signal_algo;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'uq_pain_instances_algo_breakdown'
    ) THEN
        ALTER TABLE pain_instances
        ADD CONSTRAINT uq_pain_instances_algo_breakdown
        UNIQUE (algo_version, breakdown_hash);
    END IF;
END $$;
