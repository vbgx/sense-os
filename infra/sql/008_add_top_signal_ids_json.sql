ALTER TABLE pain_clusters
ADD COLUMN IF NOT EXISTS top_signal_ids_json TEXT NOT NULL DEFAULT '[]';

CREATE INDEX IF NOT EXISTS ix_pain_clusters_top_signal_ids_json
ON pain_clusters (top_signal_ids_json);
