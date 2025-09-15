CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE documents (
    id BIGSERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    kind TEXT,
    meta JSONB,
    embedding vector(384)
);

