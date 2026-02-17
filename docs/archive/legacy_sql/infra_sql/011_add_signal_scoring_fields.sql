BEGIN;

ALTER TABLE signals
  ADD COLUMN IF NOT EXISTS signal_quality_score INTEGER,
  ADD COLUMN IF NOT EXISTS language_code VARCHAR(8),
  ADD COLUMN IF NOT EXISTS spam_score INTEGER,
  ADD COLUMN IF NOT EXISTS vertical_auto VARCHAR(64),
  ADD COLUMN IF NOT EXISTS vertical_auto_confidence INTEGER;

CREATE INDEX IF NOT EXISTS ix_signals_signal_quality_score ON signals(signal_quality_score);
CREATE INDEX IF NOT EXISTS ix_signals_language_code ON signals(language_code);
CREATE INDEX IF NOT EXISTS ix_signals_spam_score ON signals(spam_score);
CREATE INDEX IF NOT EXISTS ix_signals_vertical_auto ON signals(vertical_auto);
CREATE INDEX IF NOT EXISTS ix_signals_vertical_auto_confidence ON signals(vertical_auto_confidence);

COMMIT;
