-- Conductor Memory: Local Postgres schema (v1)

CREATE SCHEMA IF NOT EXISTS conductor_memory;

-- Extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS vector;

-- Tracks (lightweight registry)
CREATE TABLE IF NOT EXISTS conductor_memory.tracks (
  track_id TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Events (mirrors transcript.jsonl)
CREATE TABLE IF NOT EXISTS conductor_memory.events (
  track_id TEXT NOT NULL,
  seq INTEGER NOT NULL,
  event_id UUID NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  event_type TEXT NOT NULL,
  role TEXT NULL,
  content_text TEXT NULL,
  payload_json JSONB NOT NULL DEFAULT '{}'::jsonb,
  sync_policy TEXT NOT NULL DEFAULT 'sync_ok',
  contains_sensitive BOOLEAN NOT NULL DEFAULT false,
  redactions_applied BOOLEAN NOT NULL DEFAULT false,
  integrity_prev_sha256 TEXT NULL,
  integrity_sha256 TEXT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (track_id, seq),
  UNIQUE (event_id),
  CONSTRAINT events_event_type_chk CHECK (event_type IN ('message','tool_call','tool_result','artifact','note')),
  CONSTRAINT events_sync_policy_chk CHECK (sync_policy IN ('sync_ok','local_only'))
);

-- Search indexes
CREATE INDEX IF NOT EXISTS events_ts_idx ON conductor_memory.events (track_id, ts);
CREATE INDEX IF NOT EXISTS events_event_type_idx ON conductor_memory.events (track_id, event_type);

-- Full-text search over content_text
CREATE INDEX IF NOT EXISTS events_content_fts_idx
  ON conductor_memory.events
  USING GIN (to_tsvector('english', COALESCE(content_text, '')));

-- Fuzzy search over content_text
CREATE INDEX IF NOT EXISTS events_content_trgm_idx
  ON conductor_memory.events
  USING GIN (content_text gin_trgm_ops);

-- Artifacts metadata (blobs live on disk locally; remote later)
CREATE TABLE IF NOT EXISTS conductor_memory.artifacts (
  track_id TEXT NOT NULL,
  artifact_id TEXT NOT NULL,
  sha256 TEXT NOT NULL,
  media_type TEXT NOT NULL,
  relpath TEXT NOT NULL,
  size_bytes BIGINT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  PRIMARY KEY (track_id, artifact_id),
  UNIQUE (track_id, sha256)
);

-- Chunks (derived)
CREATE TABLE IF NOT EXISTS conductor_memory.chunks (
  track_id TEXT NOT NULL,
  chunk_id UUID NOT NULL,
  seq_start INTEGER NOT NULL,
  seq_end INTEGER NOT NULL,
  ts_start TIMESTAMPTZ NOT NULL,
  ts_end TIMESTAMPTZ NOT NULL,
  chunk_text TEXT NOT NULL,
  token_count INTEGER NULL,
  chunk_sha256 TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (track_id, chunk_id),
  UNIQUE (track_id, chunk_sha256)
);

CREATE INDEX IF NOT EXISTS chunks_seq_idx ON conductor_memory.chunks (track_id, seq_start, seq_end);
CREATE INDEX IF NOT EXISTS chunks_fts_idx
  ON conductor_memory.chunks
  USING GIN (to_tsvector('english', chunk_text));

-- Chunk embeddings (scaffold; not required for local MVP)
CREATE TABLE IF NOT EXISTS conductor_memory.chunk_embeddings (
  track_id TEXT NOT NULL,
  chunk_id UUID NOT NULL,
  embedder_id TEXT NOT NULL,
  embedding_dim INTEGER NOT NULL,
  embedding VECTOR(1536) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (track_id, chunk_id, embedder_id),
  CONSTRAINT chunk_embeddings_dim_chk CHECK (embedding_dim = 1536)
);

-- Summaries (derived; optional)
CREATE TABLE IF NOT EXISTS conductor_memory.summaries (
  track_id TEXT NOT NULL,
  summary_id UUID NOT NULL,
  seq_covered_end INTEGER NOT NULL,
  summary_text TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (track_id, summary_id)
);

-- Simple schema version marker
CREATE TABLE IF NOT EXISTS conductor_memory.meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);

INSERT INTO conductor_memory.meta(key, value)
VALUES ('schema_version', '1')
ON CONFLICT (key) DO NOTHING;
