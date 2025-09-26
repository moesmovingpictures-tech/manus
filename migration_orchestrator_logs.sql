-- Migration for Orchestrator Logs Table
-- Version: 1.1.2
-- Date: 2025-09-16

CREATE TABLE IF NOT EXISTS orchestrator_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    user_message TEXT NOT NULL,
    cache_hit BOOLEAN NOT NULL,
    local_model_used BOOLEAN NOT NULL,
    deepseek_used BOOLEAN NOT NULL,
    manus_used BOOLEAN NOT NULL,
    cost INTEGER NOT NULL,
    latency REAL NOT NULL,
    quality_score REAL, -- Can be NULL if not assessed
    response TEXT,
    error TEXT,
    created_at INTEGER
);

CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_timestamp ON orchestrator_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_deepseek_used ON orchestrator_logs(deepseek_used);
CREATE INDEX IF NOT EXISTS idx_orchestrator_logs_cost ON orchestrator_logs(cost);

