-- Sense OS - Indexes (V0)

BEGIN;

-- signals
CREATE INDEX IF NOT EXISTS idx_signals_vertical_id ON signals(vertical_id);
CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source);
CREATE INDEX IF NOT EXISTS idx_signals_ingested_at ON signals(ingested_at);

-- pain_instances
-- (make sure we have a vertical_id index with a name that matches %pain_instances%vertical%)
CREATE INDEX IF NOT EXISTS idx_pain_instances_vertical_id ON pain_instances(vertical_id);

CREATE INDEX IF NOT EXISTS idx_pain_instances_signal_id ON pain_instances(signal_id);
CREATE INDEX IF NOT EXISTS idx_pain_instances_score ON pain_instances(pain_score);
CREATE INDEX IF NOT EXISTS idx_pain_instances_algo_version ON pain_instances(algo_version);

COMMIT;

-- ranking / pagination helpers
CREATE INDEX IF NOT EXISTS idx_pain_instances_score_id
ON pain_instances (pain_score DESC, id ASC);

CREATE INDEX IF NOT EXISTS idx_pain_instances_vertical_score_id
ON pain_instances (vertical_id, pain_score DESC, id ASC);

-- cluster_daily_metrics
CREATE INDEX IF NOT EXISTS idx_cluster_daily_metrics_day_formula
ON cluster_daily_metrics (day, formula_version);

CREATE INDEX IF NOT EXISTS idx_cluster_daily_metrics_cluster_day
ON cluster_daily_metrics (cluster_id, day);
