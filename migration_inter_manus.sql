-- Migration for Inter-Manus Communication Feature
-- Version: 1.1.1
-- Date: 2025-09-16

-- Create sync_log table for tracking synchronization messages
CREATE TABLE IF NOT EXISTS sync_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    direction TEXT NOT NULL CHECK (direction IN ('incoming', 'outgoing')),
    message TEXT NOT NULL,
    timestamp INTEGER NOT NULL,
    processed INTEGER DEFAULT 0,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Create concepts table if it doesn't exist (for knowledge graph sync)
CREATE TABLE IF NOT EXISTS concepts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL UNIQUE,
    kind TEXT,
    meta TEXT, -- JSON metadata
    embedding TEXT, -- JSON array of floats
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    source TEXT DEFAULT 'local',
    confidence REAL DEFAULT 0.5
);

-- Create brother_metrics table for storing performance metrics from brother Manus
CREATE TABLE IF NOT EXISTS brother_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    metrics TEXT NOT NULL, -- JSON metrics data
    timestamp INTEGER NOT NULL,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Create brother_status table for storing system status from brother Manus
CREATE TABLE IF NOT EXISTS brother_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    status TEXT NOT NULL, -- JSON status data
    timestamp INTEGER NOT NULL,
    created_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Create concept_links table for relationship mapping
CREATE TABLE IF NOT EXISTS concept_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_concept_id INTEGER NOT NULL,
    to_concept_id INTEGER NOT NULL,
    relationship_type TEXT NOT NULL,
    strength REAL DEFAULT 1.0,
    created_at INTEGER DEFAULT (strftime('%s', 'now')),
    source TEXT DEFAULT 'local',
    FOREIGN KEY (from_concept_id) REFERENCES concepts(id),
    FOREIGN KEY (to_concept_id) REFERENCES concepts(id),
    UNIQUE(from_concept_id, to_concept_id, relationship_type)
);

-- Create sync_status table for tracking synchronization state
CREATE TABLE IF NOT EXISTS sync_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    last_sync_timestamp INTEGER DEFAULT 0,
    last_successful_sync INTEGER DEFAULT 0,
    sync_errors INTEGER DEFAULT 0,
    brother_manus_url TEXT,
    sync_enabled INTEGER DEFAULT 1,
    updated_at INTEGER DEFAULT (strftime('%s', 'now'))
);

-- Insert initial sync status record
INSERT OR IGNORE INTO sync_status (id, last_sync_timestamp, brother_manus_url) 
VALUES (1, 0, 'https://github.com/starsh00ter/manus_ai_smart_layer');

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_sync_log_direction_timestamp ON sync_log(direction, timestamp);
CREATE INDEX IF NOT EXISTS idx_sync_log_processed ON sync_log(processed);
CREATE INDEX IF NOT EXISTS idx_concepts_text ON concepts(text);
CREATE INDEX IF NOT EXISTS idx_concepts_created_at ON concepts(created_at);
CREATE INDEX IF NOT EXISTS idx_concepts_source ON concepts(source);
CREATE INDEX IF NOT EXISTS idx_brother_metrics_timestamp ON brother_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_brother_status_timestamp ON brother_status(timestamp);
CREATE INDEX IF NOT EXISTS idx_concept_links_from_concept ON concept_links(from_concept_id);
CREATE INDEX IF NOT EXISTS idx_concept_links_to_concept ON concept_links(to_concept_id);

-- Create view for recent sync activity
CREATE VIEW IF NOT EXISTS recent_sync_activity AS
SELECT 
    direction,
    COUNT(*) as message_count,
    MAX(timestamp) as last_message_timestamp,
    SUM(CASE WHEN processed = 1 THEN 1 ELSE 0 END) as processed_count
FROM sync_log 
WHERE timestamp > (strftime('%s', 'now') - 86400) -- Last 24 hours
GROUP BY direction;

-- Create view for concept statistics
CREATE VIEW IF NOT EXISTS concept_stats AS
SELECT 
    source,
    COUNT(*) as concept_count,
    AVG(confidence) as avg_confidence,
    MAX(created_at) as last_concept_timestamp
FROM concepts 
GROUP BY source;

-- Create view for brother Manus comparison
CREATE VIEW IF NOT EXISTS brother_comparison AS
SELECT 
    bm.source,
    bm.timestamp,
    json_extract(bm.metrics, '$.response_time_avg') as brother_response_time,
    json_extract(bm.metrics, '$.accuracy_score') as brother_accuracy,
    json_extract(bm.metrics, '$.token_efficiency') as brother_token_efficiency
FROM brother_metrics bm
WHERE bm.timestamp = (
    SELECT MAX(timestamp) FROM brother_metrics WHERE source = bm.source
);

