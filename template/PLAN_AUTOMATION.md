# Plan Automation (Canonical Plan → Conductor Tracks)

## Purpose
Conductor treats a track’s **canonical plan** as the source of truth for:
- `.conductor/tracks/<track_id>/spec.md`
- `.conductor/tracks/<track_id>/plan.md`

This document defines an automation-first workflow so that:
- A track’s canonical plan lives as repo-local markdown.
- A Conductor track can be created and kept in sync with the canonical plan.
- Changes to the canonical plan are tracked via snapshots + diffs.
- Conductor artifacts are treated as **GENERATED** (with explicitly preserved **LOCAL OVERRIDES** blocks).

## Canonical plan sources
Conductor supports one canonical plan source:
- `local_plan_markdown`: a repo-local markdown file

## Definitions
- **Canonical plan**: the designated source of truth for a track (repo-local markdown file path).
- **Snapshot**: a track-local file `canonical_plan_snapshot.md` containing an exported copy of the canonical plan at a point in time.
- **Snapshot archive**: timestamped snapshots stored under `canonical_plan_snapshots/` for historical diffing.
- **Diff archive**: timestamped diffs stored under `canonical_plan_diffs/`.
- **Generated blocks**: sections of `spec.md` / `plan.md` that are overwritten on each `update plan`.
- **Override blocks**: user-maintained sections that are never overwritten.

## Supported user commands
The agent recognizes these commands and runs the described workflow.

### 1) "create plan" / "create a plan"
Agent behavior:
- Create a repo-local canonical plan markdown file (recommended: `.conductor/tracks/<track_id>/canonical_plan.md`) and ask the user to provide the canonical plan content.

### 2) "use conductor" / "create conductor track"
Agent behavior:
- Ask for the track id (if not provided).
- Ask for the canonical plan markdown path (default: `.conductor/tracks/<track_id>/canonical_plan.md`).
- Create or update `.conductor/tracks/<track_id>/` with:
  - `metadata.json` including canonical plan identifiers (`canonical_plan_source: local_plan_markdown`, `canonical_local_plan_path`).
  - `spec.md` and `plan.md` initialized as GENERATED documents with LOCAL OVERRIDES blocks.
  - Canonical plan snapshot artifacts:
    - `canonical_plan_snapshot.md` (initial sync if possible; otherwise placeholder until first `update plan`)
    - `canonical_plan_snapshots/`
    - `canonical_plan_diffs/`
  - Create the canonical plan file if missing.

Guarantee:
- From this point on, `spec.md` and `plan.md` are treated as **generated** outputs from the canonical plan snapshot.

### 3) "update plan" / "update the plan"
Agent behavior (fully automated):

1) Sync canonical plan → snapshot
- Determine canonical plan source from `.conductor/tracks/<track_id>/metadata.json`:
  - `canonical_plan_source`: `local_plan_markdown`
- Write the new snapshot to:
  - `.conductor/tracks/<track_id>/canonical_plan_snapshot.md`
- Also write a timestamped copy into:
  - `.conductor/tracks/<track_id>/canonical_plan_snapshots/<YYYYMMDD_HHMMSSZ>.md`

2) Diff tracking
- Write a diff file comparing the *previous* snapshot to the *new* snapshot:
  - `.conductor/tracks/<track_id>/canonical_plan_diffs/<YYYYMMDD_HHMMSSZ>.diff`
- Show the diff to the user (review step).

3) Regenerate Conductor artifacts
- Rewrite only the GENERATED blocks in:
  - `spec.md`
  - `plan.md`
- Compute / refresh the **Token & Cost Estimate (Generated)** section in `plan.md`.
  - Raw token estimates must always be produced.
  - USD estimates must be blocked (but raw tokens still shown) if `.conductor/llm_pricing.json` is missing or lacks the requested provider/model.
  - Cache-aware USD must always include a scenario range at cache_hit_rate = 0.0 / 0.5 / 1.0.
- Preserve LOCAL OVERRIDES blocks byte-for-byte.

4) Update metadata
Update `.conductor/tracks/<track_id>/metadata.json` with:
- `canonical_plan_source`
- Pointer fields:
  - `canonical_local_plan_path`
- Snapshot bookkeeping:
  - `canonical_plan_snapshot_path`
  - `canonical_plan_snapshot_generated_at`
  - `canonical_plan_snapshot_sha256`
  - `last_sync_status`: `ok` or `error`

Hard stop rule:
- If the snapshot cannot be generated (canonical plan not accessible), the agent must STOP and report what is missing.

### 4) "scan plan" / "scan the plan"
Agent behavior:
- Ask for the track id (if not provided).
- Read the canonical plan markdown and cross-check it against the track `spec.md` and `plan.md`.
- Produce a structured scan report in chat (do not write files unless the user asks to "save scan report").

### 5) "execute plan" / "execute the plan" / "implement the plan"
Agent behavior:
- Recommend running "scan plan" first (optional but recommended).
- Read the track `spec.md` + `plan.md`.
- Implement tasks phase-by-phase per `.conductor/workflow.md`.
- Stop at checkpoints.

### 6) "save scan report"
Agent behavior:
- Save the most recent scan report to `.conductor/tracks/<track_id>/plan_scans/<YYYYMMDD_HHMMSSZ>.md`.
- If no scan has been run yet, run "scan plan" first, then save.

## Track file layout (required)
Each track directory uses this layout:
- `.conductor/tracks/<track_id>/metadata.json`
- `.conductor/tracks/<track_id>/spec.md`
- `.conductor/tracks/<track_id>/plan.md`
- `.conductor/tracks/<track_id>/canonical_plan_snapshot.md`
- `.conductor/tracks/<track_id>/canonical_plan_snapshots/`
- `.conductor/tracks/<track_id>/canonical_plan_diffs/`

Recommended
- `.conductor/tracks/<track_id>/canonical_plan.md`

## Generated vs Override blocks (required)
`spec.md` and `plan.md` must contain both of these blocks:

- GENERATED block (rewritten on `update plan`):
  - Between markers:
    - `<!-- BEGIN GENERATED -->`
    - `<!-- END GENERATED -->`

- LOCAL OVERRIDES block (never overwritten):
  - Between markers:
    - `<!-- BEGIN LOCAL OVERRIDES -->`
    - `<!-- END LOCAL OVERRIDES -->`

Rules:
- Users may edit LOCAL OVERRIDES freely.
- Users should not edit GENERATED blocks directly.

## Token + Cost Estimation (required)
The generated `plan.md` must include a **Token & Cost Estimate (Generated)** section.

Config files
- Estimator defaults: `.conductor/llm_estimator_defaults.json`
- Pricing (required for USD section): `.conductor/llm_pricing.json`
- Calibration samples (optional): `.conductor/llm_usage_samples.jsonl`

Rules
- Raw token estimates must always be present.
- USD estimates are shown only when pricing is available; otherwise the USD section must be clearly marked as BLOCKED (missing pricing).
- Cache-aware USD must always be shown as a scenario range at cache_hit_rate = 0.0 / 0.5 / 1.0.
- If `.conductor/llm_usage_samples.jsonl` contains samples, use them to calibrate defaults in `.conductor/llm_estimator_defaults.json` (per provider/model).

## How canonical plans are read
Local markdown (`local_plan_markdown`)
- The canonical plan is a normal file in the repo.
- The agent reads it directly.

## Non-goals
- This workflow does not attempt to auto-sync on every canonical plan edit (no push/webhook assumption). The explicit trigger is `update plan`.
- This workflow does not auto-commit changes. Snapshot/diff tracking is done via files; commits are optional and must be explicitly requested.
