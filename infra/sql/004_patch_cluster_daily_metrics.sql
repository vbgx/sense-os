BEGIN;

ALTER TABLE cluster_daily_metrics
  ADD COLUMN IF NOT EXISTS score double precision NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS score_volume double precision NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS score_velocity double precision NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS score_novelty double precision NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS score_diversity double precision NOT NULL DEFAULT 0.0,
  ADD COLUMN IF NOT EXISTS score_confidence double precision NOT NULL DEFAULT 0.0;

UPDATE cluster_daily_metrics
SET
  score = COALESCE(score, 0.0),
  score_volume = COALESCE(score_volume, 0.0),
  score_velocity = COALESCE(score_velocity, 0.0),
  score_novelty = COALESCE(score_novelty, 0.0),
  score_diversity = COALESCE(score_diversity, 0.0),
  score_confidence = COALESCE(score_confidence, 0.0);

COMMIT;
