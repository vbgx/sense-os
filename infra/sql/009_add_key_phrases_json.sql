ALTER TABLE pain_clusters
ADD COLUMN IF NOT EXISTS key_phrases_json TEXT NOT NULL DEFAULT '[]';

CREATE INDEX IF NOT EXISTS ix_pain_clusters_key_phrases_json
ON pain_clusters (key_phrases_json);
