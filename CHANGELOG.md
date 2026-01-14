# Changelog

Conductor Kit follows Semantic Versioning (SemVer).

- Patch: bug fixes / safe improvements
- Minor: backwards-compatible features
- Major: breaking changes (see BREAKING CHANGES notes below and `UPGRADING.md`)

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
