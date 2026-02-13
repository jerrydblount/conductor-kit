# Changelog

Conductor Kit follows Semantic Versioning (SemVer).

- Patch: bug fixes / safe improvements
- Minor: backwards-compatible features
- Major: breaking changes (see BREAKING CHANGES notes below and `UPGRADING.md`)

## [0.3.0] - 2026-02-12

Added:
- Conductor Memory (local MVP): lossless per-track transcript JSONL + state.
- New CLI commands:
  - `conductor memory append`
  - `conductor memory summarize`
  - `conductor memory backfill-db`
  - `conductor memory sync` (stub)
  - `conductor memory db {up,down,status,migrate,psql}`
- Repo template additions under `.conductor/memory/` (config, docker compose, SQL migrations).
- `.conductor/.gitignore` defaults to keep lossless transcripts and tool artifacts uncommitted.

Changed:
- `conductor doctor` now checks Memory template files and prints advisory local DB dependency status.

## [0.2.0] - 2026-01-24

Added:
- Added plan scanning commands: "scan plan" (in-chat report) and "save scan report" (optional repo-local report file).

Changed:
- Removed Warp notebook as a canonical plan source. Canonical plans are now repo-local markdown only (`local_plan_markdown`).

## [0.1.0] - 2026-01-14

Initial release.

Added:
- Repo-local Conductor template under `template/`
- CLI at `bin/conductor`:
  - `init`, `upgrade`, `version`, `doctor`, `integrate`
- IDE integrations:
  - Warp global loader rule template
  - Cursor `.cursorrules` template
  - Generic `AGENTS.md` template

Notes:
- Canonical plan snapshots/diffs use generic `canonical_plan_*` names.
- `.conductor/product.md` and `.conductor/tech-stack.md` are treated as project-owned and are not overwritten by default.
