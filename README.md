# Conductor Kit

Conductor Kit is a port of the Gemini CLI extension [Conductor](https://geminicli.com/extensions/?name=gemini-cli-extensionsconductor). This is not a 1:1, rather it's a very close recreation with some modifications and additional features. 
The goal of Conductor Kit is to enable non-Gemini CLI users to benefit from the context-driven approach. 
Conductor Kit supports Warp, Cursor, or any agentic IDE.

Conductor Kit is a repo-local, IDE-agnostic way to run context-driven development:
- You keep the workflow, product context, and tech constraints in the repo under `.conductor/`.
- Work is organized into **tracks** (`.conductor/tracks/<track-name>/`) with a `spec.md`, `plan.md`, and `metadata.json`.
- Plans are captured in a **canonical plan** format (Warp notebook or local markdown) and converted into Conductor tracks.
- The system produces durable artifacts (snapshots and diffs) so work is auditable and repeatable.

This repository contains:
- A **template** (`template/`) that gets installed into any target repo.
- A **CLI** (`bin/conductor`) to install, upgrade, and validate the installation.
- **IDE integrations** (`integrations/`) for Warp, Cursor, and a generic “AGENTS.md” setup.

## Key concepts

### Repo-local source of truth
The `.conductor/` directory is the source of truth for how Conductor operates in a repo.

### Canonical plan
Conductor supports two canonical plan sources:
- `warp_notebook`: a Warp-native plan format (machine-readable in Warp)
- `local_plan_markdown`: a plain markdown plan (works anywhere)

The canonical plan is snapshotted and diffed using generic names (required for all IDEs):
- `canonical_plan_snapshot.md`
- `canonical_plan_snapshots/`
- `canonical_plan_diffs/`

New installs should use the `canonical_plan_*` names. The template documentation also describes backward compatibility for older `warp_plan_*` names.

### Managed vs project-owned files
Conductor Kit manages and upgrades these files:
- `.conductor/CONDUCTOR.md`
- `.conductor/CONDUCTOR_README.md`
- `.conductor/workflow.md`
- `.conductor/llm_estimator_defaults.json`
- `.conductor/llm_pricing.json`
- `.conductor/llm_usage_samples.jsonl`
- `.conductor/conductor_version.json` (installed version stamp)
- `PLAN_AUTOMATION.md`

These are project-owned and are NOT overwritten by default:
- `.conductor/product.md`
- `.conductor/tech-stack.md`
- `.conductor/tracks/**`

## Installation

### 1) Get the CLI
Clone this repo somewhere on your machine (or keep it as a submodule). You can run the CLI directly:
- `python3 /path/to/conductor-kit/bin/conductor ...`

Optional: put `bin/conductor` on your PATH as `conductor` (symlink, copy, or shell alias).

### 2) Install Conductor into a repo
From anywhere:
- `conductor init /path/to/your-repo`

This will create:
- `.conductor/` (plus `tracks/` and `archive/`)
- Conductor-managed workflow/config files
- project-owned placeholders for `product.md` and `tech-stack.md` (only if missing)
- `PLAN_AUTOMATION.md`

### 3) Add IDE integration (choose one)

#### Warp (global loader rule)
Warp uses a single global rule that delegates to the repo-local `.conductor/CONDUCTOR.md`.
- Copy/paste the template at `integrations/warp/conductor-loader-rule.txt` into Warp’s global rules.

Important:
- This Warp global rule is NOT installed or upgraded by `conductor init` / `conductor upgrade`.
- If the template loader rule changes in future Conductor Kit releases, updating Warp is manual: re-copy/paste.

#### Cursor
Install a repo-local `.cursorrules`:
- `conductor integrate cursor /path/to/your-repo`

#### Generic (any IDE/editor)
Install a repo-local `AGENTS.md`:
- `conductor integrate generic /path/to/your-repo`

## Usage

1) In your IDE, explicitly opt into Conductor (examples):
- “Start a new track: <name>”
- “Use Conductor to update the plan”
- “Execute the plan for track <name>”

2) The assistant should read and follow `.conductor/CONDUCTOR.md`.

3) Conductor’s workflow and plan automation rules live in:
- `.conductor/workflow.md`
- `PLAN_AUTOMATION.md`

## Upgrade

To upgrade a repo’s Conductor-managed files:
- `conductor upgrade /path/to/your-repo`

By default, upgrades:
- update Conductor-managed files
- do NOT overwrite `.conductor/product.md` or `.conductor/tech-stack.md`
- never touch `.conductor/tracks/**`

To overwrite project-owned context (with diff + backup + confirmation):
- `conductor upgrade /path/to/your-repo --overwrite-product`
- `conductor upgrade /path/to/your-repo --overwrite-techstack`

Major upgrades require an explicit flag:
- `conductor upgrade /path/to/your-repo --accept-breaking`

See `CHANGELOG.md` and `UPGRADING.md`.

## CLI reference

- `conductor init [path]`
- `conductor upgrade [path]`
- `conductor version [path]`
- `conductor doctor [path]`
- `conductor integrate {warp|cursor|generic} [path]`

## Notes

- Conductor is opt-in: integrations are written to activate only when the user explicitly requests Conductor behavior.
- Conductor-managed directories like `.conductor/tracks/` and `.conductor/archive/` are created on install (no `.gitkeep` files required).
