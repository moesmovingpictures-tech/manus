-- Indexes for conv_turn table
CREATE INDEX IF NOT EXISTS idx_conv_turn_ts ON conv_turn (ts);
CREATE INDEX IF NOT EXISTS idx_conv_turn_role ON conv_turn (role);

-- Indexes for concept table
CREATE INDEX IF NOT EXISTS idx_concept_name ON concept (name);

-- Indexes for debug_log table
CREATE INDEX IF NOT EXISTS idx_debug_log_ts ON debug_log (ts);
CREATE INDEX IF NOT EXISTS idx_debug_log_source ON debug_log (source);
CREATE INDEX IF NOT EXISTS idx_debug_log_level ON debug_log (level);


