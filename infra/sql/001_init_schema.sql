BEGIN;

-- --------------------------------------------
-- verticals
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS verticals (
  id         SERIAL PRIMARY KEY,
  name       VARCHAR(255) NOT NULL UNIQUE,
  created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);

-- --------------------------------------------
-- signals
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS signals (
  id          SERIAL PRIMARY KEY,
  vertical_id INTEGER     NOT NULL REFERENCES verticals(id) ON DELETE CASCADE,
  source      VARCHAR(64) NOT NULL,
  external_id VARCHAR(255) NOT NULL,
  content     TEXT        NOT NULL,
  url         TEXT        NULL,
  created_at  TIMESTAMPTZ NULL,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_signals_source_external_id UNIQUE (source, external_id)
);

CREATE INDEX IF NOT EXISTS ix_signals_vertical_id ON signals(vertical_id);
CREATE INDEX IF NOT EXISTS ix_signals_ingested_at ON signals(ingested_at);

-- --------------------------------------------
-- pain_instances  ✅ must include vertical_id
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS pain_instances (
  id          SERIAL PRIMARY KEY,
  vertical_id INTEGER     NOT NULL REFERENCES verticals(id) ON DELETE CASCADE,
  signal_id   INTEGER     NOT NULL REFERENCES signals(id)   ON DELETE CASCADE,
  algo_version VARCHAR(64) NOT NULL,
  pain_score  DOUBLE PRECISION NOT NULL,
  breakdown   JSONB       NOT NULL DEFAULT '{}'::jsonb,
  breakdown_hash VARCHAR(32) NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_pain_instances_algo_breakdown UNIQUE (algo_version, breakdown_hash)
);

CREATE INDEX IF NOT EXISTS ix_pain_instances_vertical_id ON pain_instances(vertical_id);
CREATE INDEX IF NOT EXISTS ix_pain_instances_signal_id ON pain_instances(signal_id);

-- --------------------------------------------
-- pain_clusters
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS pain_clusters (
  id             SERIAL PRIMARY KEY,
  vertical_id    INTEGER     NOT NULL REFERENCES verticals(id) ON DELETE CASCADE,
  cluster_version VARCHAR(64) NOT NULL,
  cluster_key    VARCHAR(64) NOT NULL,
  title          VARCHAR(255) NOT NULL,
  size           INTEGER     NOT NULL DEFAULT 0,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_pain_clusters_version_key UNIQUE (vertical_id, cluster_version, cluster_key)
);

CREATE INDEX IF NOT EXISTS ix_pain_clusters_vertical_version ON pain_clusters(vertical_id, cluster_version);

-- --------------------------------------------
-- cluster_signals
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS cluster_signals (
  id               SERIAL PRIMARY KEY,
  cluster_id       INTEGER NOT NULL REFERENCES pain_clusters(id)  ON DELETE CASCADE,
  pain_instance_id INTEGER NOT NULL REFERENCES pain_instances(id) ON DELETE CASCADE,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT uq_cluster_signals_cluster_pain UNIQUE (cluster_id, pain_instance_id)
);

CREATE INDEX IF NOT EXISTS ix_cluster_signals_cluster_id ON cluster_signals(cluster_id);
CREATE INDEX IF NOT EXISTS ix_cluster_signals_pain_instance_id ON cluster_signals(pain_instance_id);

-- --------------------------------------------
-- cluster_daily_metrics
-- --------------------------------------------
CREATE TABLE IF NOT EXISTS cluster_daily_metrics (
  id              SERIAL PRIMARY KEY,
  cluster_id      INTEGER NOT NULL REFERENCES pain_clusters(id) ON DELETE CASCADE,
  day             DATE    NOT NULL,
  formula_version VARCHAR(64) NOT NULL,

  frequency   INTEGER NOT NULL DEFAULT 0,
  engagement  INTEGER NOT NULL DEFAULT 0,
  avg_score   DOUBLE PRECISION NOT NULL DEFAULT 0.0,
  source_count INTEGER NOT NULL DEFAULT 0,

  velocity   DOUBLE PRECISION NOT NULL DEFAULT 0.0,
  emerging   DOUBLE PRECISION NOT NULL DEFAULT 0.0,
  declining  DOUBLE PRECISION NOT NULL DEFAULT 0.0,

  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

  CONSTRAINT uq_cluster_daily_metrics_cluster_day_formula UNIQUE (cluster_id, day, formula_version)
);

CREATE INDEX IF NOT EXISTS ix_cluster_daily_metrics_day ON cluster_daily_metrics(day);
CREATE INDEX IF NOT EXISTS ix_cluster_daily_metrics_cluster_day ON cluster_daily_metrics(cluster_id, day);

COMMIT;
