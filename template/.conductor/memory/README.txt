Conductor Memory (local MVP)

This directory contains repo-local configuration for Conductor's lossless conversation transcript capture and optional local indexing.

Canonical transcript (per track)
- .conductor/tracks/<track_id>/memory/transcript.jsonl   (append-only; lossless)
- .conductor/tracks/<track_id>/memory/state.json         (cursors; seq assignment)
- .conductor/tracks/<track_id>/memory/artifacts/         (large tool outputs and other blobs)

Local DB (optional acceleration index)
- docker-compose.yml starts a local Postgres instance (with pgvector installed for future use).
- migrations/001_init.sql creates tables + indexes (FTS + trigram) and scaffolds vector tables.

Getting started
1) Start the DB:
   conductor memory db up
2) Apply migrations:
   conductor memory db migrate
3) Backfill transcript events into Postgres:
   conductor memory backfill-db --all-tracks

Notes
- Conductor's canonical transcript persistence does not require Postgres.
- The local DB is rebuildable from transcript.jsonl.
