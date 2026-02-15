# Plan Automation (Canonical Plan → Conductor Tracks)

## Purpose
Conductor treats a track’s **canonical plan** as the source of truth for:
- `.conductor/tracks/<track_id>/spec.md`
- `.conductor/tracks/<track_id>/plan.md`

This document defines an automation-first workflow so that:
- A track’s canonical plan can be chosen (Warp notebook or local markdown).
- A Conductor track can be created and kept in sync with the canonical plan.
- Changes to the canonical plan are tracked via snapshots + diffs.
- Conductor artifacts are treated as **GENERATED** (with explicitly preserved **LOCAL OVERRIDES** blocks).

## Canonical plan sources
Conductor supports two canonical plan sources:
- `warp_notebook`: a Warp Drive notebook URL/ID
- `local_plan_markdown`: a repo-local markdown file

## Definitions
- **Canonical plan**: the designated source of truth for a track (Warp notebook URL/ID or local markdown file path).
- **Snapshot**: a track-local file `canonical_plan_snapshot.md` containing an exported copy of the canonical plan at a point in time.
- **Snapshot archive**: timestamped snapshots stored under `canonical_plan_snapshots/` for historical diffing.
- **Diff archive**: timestamped diffs stored under `canonical_plan_diffs/`.
- **Generated blocks**: sections of `spec.md` / `plan.md` that are overwritten on each `update plan`.
- **Override blocks**: user-maintained sections that are never overwritten.

## Supported user commands
The agent recognizes these commands and runs the described workflow.

### 1) "create plan" / "create a plan"
Agent behavior:
- Ask the user which canonical plan source to use:
  - Warp notebook (`warp_notebook`)
  - Local markdown (`local_plan_markdown`)
- If Warp notebook is chosen and a Warp Drive notebook URL is produced/shared, treat it as canonical and derive the notebook ID.
- If local markdown is chosen, create a canonical plan file path (recommended: `.conductor/tracks/<track_id>/canonical_plan.md`) and ask the user to provide the canonical plan content.

Warp notebook notes:
- Canonical plan form is a Warp Drive notebook URL like:
  `https://app.warp.dev/drive/notebook/<title>-<NOTEBOOK_ID>`
- The notebook ID is the trailing token.

### 2) "use conductor" / "create conductor track"
Agent behavior:
- Ask for the track id (if not provided).
- Ask for the canonical plan source (`warp_notebook` or `local_plan_markdown`) and capture the appropriate pointer fields.
- Create or update `.conductor/tracks/<track_id>/` with:
  - `metadata.json` including canonical plan identifiers.
  - `spec.md` and `plan.md` initialized as GENERATED documents with LOCAL OVERRIDES blocks.
  - Canonical plan snapshot artifacts:
    - `canonical_plan_snapshot.md` (initial sync if possible; otherwise placeholder until first `update plan`)
    - `canonical_plan_snapshots/`
    - `canonical_plan_diffs/`
  - If `local_plan_markdown`: create the canonical plan file (recommended: `canonical_plan.md`) if missing.

Guarantee:
- From this point on, `spec.md` and `plan.md` are treated as **generated** outputs from the canonical plan snapshot.

### 3) "update plan" / "update the plan"
Agent behavior (fully automated):

1) Sync canonical plan → snapshot
- Determine canonical plan source from `.conductor/tracks/<track_id>/metadata.json`:
  - `canonical_plan_source`: `warp_notebook` | `local_plan_markdown`
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
- Preserve LOCAL OVERRIDES blocks byte-for-byte.

4) Update metadata
Update `.conductor/tracks/<track_id>/metadata.json` with:
- `canonical_plan_source`
- Pointer fields for the canonical plan source:
  - If `warp_notebook`: `canonical_warp_plan_url`, `canonical_warp_notebook_id`
  - If `local_plan_markdown`: `canonical_local_plan_path`
- Snapshot bookkeeping:
  - `canonical_plan_snapshot_path`
  - `canonical_plan_snapshot_generated_at`
  - `canonical_plan_snapshot_sha256`
  - `last_sync_status`: `ok` or `error`

Hard stop rule:
- If the snapshot cannot be generated (canonical plan not accessible), the agent must STOP and report what is missing.

### 4) "execute plan" / "execute the plan" / "implement the plan"
Agent behavior:
- Read the track `spec.md` + `plan.md`.
- Implement tasks phase-by-phase per `.conductor/workflow.md`.
- Stop at checkpoints.

## Track file layout (required)
Each track directory uses this layout:
- `.conductor/tracks/<track_id>/metadata.json`
- `.conductor/tracks/<track_id>/spec.md`
- `.conductor/tracks/<track_id>/plan.md`
- `.conductor/tracks/<track_id>/canonical_plan_snapshot.md`
- `.conductor/tracks/<track_id>/canonical_plan_snapshots/`
- `.conductor/tracks/<track_id>/canonical_plan_diffs/`

Optional (recommended)
- If `local_plan_markdown`:
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

## How canonical plans become machine-readable
Warp notebook (`warp_notebook`)
- The canonical plan is a Warp Drive notebook URL (JS-gated in a browser).
- The agent treats it as machine-readable via Warp’s ability to attach notebook content by ID (e.g., `<notebook:<id>>`) during an agent run.

Local markdown (`local_plan_markdown`)
- The canonical plan is a normal file in the repo.
- The agent reads it directly.

## Non-goals
- This workflow does not attempt to auto-sync on every canonical plan edit (no push/webhook assumption). The explicit trigger is `update plan`.
- This workflow does not auto-commit changes. Snapshot/diff tracking is done via files; commits are optional and must be explicitly requested.
