BEGIN;

ALTER TABLE pain_clusters
  ADD COLUMN IF NOT EXISTS severity_score INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS recurrence_score INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS recurrence_ratio DOUBLE PRECISION NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS dominant_persona TEXT NOT NULL DEFAULT 'unknown',
  ADD COLUMN IF NOT EXISTS persona_confidence DOUBLE PRECISION NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS persona_distribution_json TEXT NOT NULL DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS monetizability_score INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS contradiction_score INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS breakout_score INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS saturation_score INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS opportunity_window_score INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS opportunity_window_status TEXT NOT NULL DEFAULT 'UNKNOWN',
  ADD COLUMN IF NOT EXISTS half_life_days DOUBLE PRECISION NULL,
  ADD COLUMN IF NOT EXISTS competitive_heat_score INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS exploitability_score INTEGER NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS exploitability_pain_strength DOUBLE PRECISION NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS exploitability_timing_strength DOUBLE PRECISION NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS exploitability_risk_penalty DOUBLE PRECISION NOT NULL DEFAULT 0,
  ADD COLUMN IF NOT EXISTS exploitability_version TEXT NOT NULL DEFAULT '',
  ADD COLUMN IF NOT EXISTS exploitability_tier TEXT NOT NULL DEFAULT 'IGNORE',
  ADD COLUMN IF NOT EXISTS cluster_summary TEXT,
  ADD COLUMN IF NOT EXISTS top_signal_ids_json TEXT NOT NULL DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS key_phrases_json TEXT NOT NULL DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS confidence_score INTEGER NOT NULL DEFAULT 0;

CREATE INDEX IF NOT EXISTS ix_pain_clusters_severity_score ON pain_clusters(severity_score);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_recurrence_score ON pain_clusters(recurrence_score);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_dominant_persona ON pain_clusters(dominant_persona);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_monetizability_score ON pain_clusters(monetizability_score);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_contradiction_score ON pain_clusters(contradiction_score);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_breakout_score ON pain_clusters(breakout_score);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_saturation_score ON pain_clusters(saturation_score);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_opportunity_window_score ON pain_clusters(opportunity_window_score);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_opportunity_window_status ON pain_clusters(opportunity_window_status);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_half_life_days ON pain_clusters(half_life_days);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_competitive_heat_score ON pain_clusters(competitive_heat_score);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_exploitability_score ON pain_clusters(exploitability_score);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_exploitability_version ON pain_clusters(exploitability_version);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_exploitability_tier ON pain_clusters(exploitability_tier);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_top_signal_ids_json ON pain_clusters(top_signal_ids_json);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_key_phrases_json ON pain_clusters(key_phrases_json);
CREATE INDEX IF NOT EXISTS ix_pain_clusters_confidence_score ON pain_clusters(confidence_score);

COMMIT;
