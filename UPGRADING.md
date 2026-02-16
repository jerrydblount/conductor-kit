# Upgrading Conductor

This document describes how Conductor Kit upgrades work, what gets upgraded automatically, and what requires manual steps.

## Quick guide

Upgrade a repo:
- `conductor upgrade /path/to/your-repo`

If upgrading across a MAJOR version:
- Read `CHANGELOG.md`
- Then run: `conductor upgrade /path/to/your-repo --accept-breaking`

## What Conductor upgrades (managed files)

Conductor Kit treats these files as Conductor-managed and safe to upgrade:
- `.conductor/CONDUCTOR.md`
- `.conductor/CONDUCTOR_README.md`
- `.conductor/workflow.md`
- `.conductor/.gitignore`
- `.conductor/memory/config.json`
- `.conductor/memory/docker-compose.yml`
- `.conductor/memory/README.txt`
- `.conductor/memory/migrations/001_init.sql`
- `PLAN_AUTOMATION.md`
- `.conductor/conductor_version.json`

On upgrade, the CLI will show diffs and ask for confirmation before overwriting any existing file.
Use `--yes` to auto-confirm prompts.

## What Conductor does NOT upgrade by default (project-owned)

These are treated as owned by the project and are NOT overwritten by default:
- `.conductor/product.md`
- `.conductor/tech-stack.md`
- `.conductor/tracks/**`

### Overwriting product/tech-stack (explicit)

If you want to reset/overwrite these from the template, you must opt in:
- `conductor upgrade /path/to/your-repo --overwrite-product`
- `conductor upgrade /path/to/your-repo --overwrite-techstack`

When overwriting:
- The CLI shows a unified diff
- It asks for confirmation
- It backs up the prior file under `.conductor/archive/context_backups/<timestamp>/`

## Tracks and archive directories

Conductor creates these directories if missing:
- `.conductor/tracks/`
- `.conductor/archive/`

No `.gitkeep` files are required. Empty directories are created during `init` / `upgrade`.

## Warp loader rule (manual)

Warp integration uses a single global “loader rule” that delegates to repo-local `.conductor/CONDUCTOR.md`.

Important:
- The Warp global rule is stored in Warp settings.
- `conductor init` / `conductor upgrade` cannot modify Warp’s global rules.
- If the Warp loader template changes in future Conductor Kit releases, updating Warp is manual:
  - re-copy/paste from `integrations/warp/conductor-loader-rule.txt`

## Recovering / reinstalling

If `.conductor/` was deleted or partially lost:
- Re-run `conductor init /path/to/your-repo`.

This will recreate missing managed files and directories.
If you still have `.conductor/tracks/**`, they will be preserved.

## Notes on versioning

- Installed version is stored in `.conductor/conductor_version.json`.
- `conductor version` prints the installed version.
- `conductor doctor` checks required files and can flag drift.
