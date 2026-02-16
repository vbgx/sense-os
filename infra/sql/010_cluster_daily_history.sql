CREATE TABLE IF NOT EXISTS cluster_daily_history (
  cluster_id TEXT NOT NULL,
  day DATE NOT NULL,
  volume INTEGER NOT NULL DEFAULT 0,
  growth_rate DOUBLE PRECISION NOT NULL DEFAULT 0,
  velocity DOUBLE PRECISION NOT NULL DEFAULT 0,
  breakout_flag BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  PRIMARY KEY (cluster_id, day)
);

CREATE INDEX IF NOT EXISTS ix_cluster_daily_history_cluster_day
ON cluster_daily_history (cluster_id, day);
