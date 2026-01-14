# Conductor Kit

Conductor Kit is a port of the Gemini CLI extension [Conductor](https://geminicli.com/extensions/?name=gemini-cli-extensionsconductor). This is not a 1:1, rather it's a close recreation with some modifications and additional features. 
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
- **IDE integrations** (`integrations/`) for Warp, Cursor, and a generic "AGENTS.md" setup.

---

## Installation

Installing Conductor is a two-part process:
1. **Part A**: Get the Conductor Kit CLI onto your machine (do this once).
2. **Part B**: Use that CLI to install Conductor into each project repo you want to use it in.

---

### Part A: Install Conductor Kit (the CLI) — do this once

#### Step A1: Clone the conductor-kit repository

Pick a permanent location on your machine. For example:

```sh
git clone https://github.com/jerrydblount/conductor-kit.git ~/conductor-kit
```

You can choose any path you like; just remember it.

#### Step A2: Verify the CLI runs

```sh
python3 ~/conductor-kit/bin/conductor --help
```

You should see output like:

```
usage: conductor [-h] [--dry-run] [--yes] {init,upgrade,version,doctor,integrate} ...
```

If that works, Conductor Kit is installed.

---

### Part B: Install Conductor into a project repo

Repeat these steps for each repo where you want to use Conductor.

#### Step B1: Run `conductor init`

From anywhere, run:

```sh
python3 ~/conductor-kit/bin/conductor init /path/to/your-project
```

Or, if you are already in the project root:

```sh
python3 ~/conductor-kit/bin/conductor init .
```

This creates:
- `.conductor/` directory with:
  - `CONDUCTOR.md` (the master rule that guides your AI assistant)
  - `workflow.md`, `CONDUCTOR_README.md`, config files
  - `tracks/` (where track folders will live)
  - `archive/` (used for backups)
  - `product.md` (placeholder — populated by the AI assistant)
  - `tech-stack.md` (placeholder — populated by the AI assistant)
- `PLAN_AUTOMATION.md` at the repo root

#### Step B2: Add IDE integration (choose one)

**For Warp (global loader rule — manual setup)**

Warp uses a single global rule that delegates to the repo-local `.conductor/CONDUCTOR.md`.

1. Run this to see the rule text:
   ```sh
   python3 ~/conductor-kit/bin/conductor integrate warp
   ```
2. Copy the printed text.
3. Paste it into Warp's global rules (Warp Settings → Rules).

Note: This is a one-time manual step. `conductor init` / `conductor upgrade` cannot modify Warp's global rules. If the template changes in future releases, you must re-copy/paste.

**For Cursor (repo-local)**

```sh
python3 ~/conductor-kit/bin/conductor integrate cursor /path/to/your-project
```

This creates `.cursorrules` in your project.

**For other IDEs / generic (repo-local)**

```sh
python3 ~/conductor-kit/bin/conductor integrate generic /path/to/your-project
```

This creates `AGENTS.md` in your project.

#### Step B3: Verify the installation

```sh
python3 ~/conductor-kit/bin/conductor doctor /path/to/your-project
```

You should see `OK` for all required files and directories.

```sh
python3 ~/conductor-kit/bin/conductor version /path/to/your-project
```

Shows the installed Conductor version.

---

## Usage

Conductor is opt-in. It only activates when you explicitly trigger it.

### Trigger phrases

The assistant will engage Conductor when you say:
- "Start a new track" / "Create conductor track"
- "Use Conductor"
- "Update plan" / "Update the plan"
- "Execute plan" / "Execute the plan" / "Implement the plan"
- Or reference a Conductor artifact (e.g., "Check the spec for track X")

If you don't use a trigger phrase, the assistant behaves normally.

### The workflow

#### 1. Start a track

Say: "Start a new track for [Feature Name]"

The assistant will:
1. Create a track directory (`.conductor/tracks/<track_id>/`)
2. Ask you to choose a canonical plan source (`warp_notebook` or `local_plan_markdown`)
3. Interview you to gather requirements (goal, functional/non-functional requirements, out of scope, acceptance criteria)
4. Generate `spec.md`

#### 2. Plan

Once the spec is ready, the assistant will:
1. Generate `plan.md` based on the spec and canonical plan
2. Break down work into phases and tasks
3. Add phase checkpoints for manual verification
4. Include token/cost estimates

#### 3. Implement

Say: "Execute the plan" or "Implement track <track_id>"

The assistant will:
1. Follow the TDD workflow (Red → Green → Refactor) defined in `.conductor/workflow.md`
2. Update `plan.md` task statuses as it progresses (`[ ]` → `[~]` → `[x]`)
3. Stop at phase checkpoints for you to verify before continuing

#### 4. Finalize

When the track is complete:
1. The assistant may propose updates to `product.md` and `tech-stack.md` if the track changed product scope or introduced new tech
2. The track can be archived to `.conductor/archive/`

### Updating a plan

If you modify the canonical plan (Warp notebook or local markdown), say: "Update the plan"

The assistant will sync the canonical plan into the track, regenerate `spec.md` and `plan.md` (preserving any local overrides), and record a diff.

---

## Upgrading

To upgrade Conductor-managed files in an existing repo:

```sh
conductor upgrade /path/to/your-project
```

By default:
- Updates Conductor-managed files
- Does NOT overwrite `.conductor/product.md` or `.conductor/tech-stack.md`
- Never touches `.conductor/tracks/**`

To overwrite project-owned context (shows diff, backs up, asks for confirmation):

```sh
conductor upgrade /path/to/your-project --overwrite-product
conductor upgrade /path/to/your-project --overwrite-techstack
```

For major version upgrades (breaking changes):

```sh
conductor upgrade /path/to/your-project --accept-breaking
```

See `CHANGELOG.md` and `UPGRADING.md` for details.

---

## CLI Reference

| Command | Description |
|---------|-------------|
| `conductor init [path]` | Install Conductor into a repo |
| `conductor upgrade [path]` | Upgrade Conductor-managed files |
| `conductor version [path]` | Print installed version |
| `conductor doctor [path]` | Check installation health |
| `conductor integrate {warp,cursor,generic} [path]` | Install IDE integration |

All commands accept `--dry-run` (print actions without writing) and `--yes` (auto-confirm prompts).

---

## Key Concepts

### Repo-local source of truth
The `.conductor/` directory is the source of truth for how Conductor operates in a repo.

### Canonical plan
Conductor supports two canonical plan sources:
- `warp_notebook`: a Warp-native plan format (machine-readable in Warp)
- `local_plan_markdown`: a plain markdown plan (works anywhere)

Snapshots and diffs use generic names:
- `canonical_plan_snapshot.md`
- `canonical_plan_snapshots/`
- `canonical_plan_diffs/`

### Managed vs project-owned files

**Conductor-managed** (updated by `conductor upgrade`):
- `.conductor/CONDUCTOR.md`
- `.conductor/CONDUCTOR_README.md`
- `.conductor/workflow.md`
- `.conductor/llm_*.json` / `.jsonl`
- `.conductor/conductor_version.json`
- `PLAN_AUTOMATION.md`

**Project-owned** (NOT overwritten by default):
- `.conductor/product.md`
- `.conductor/tech-stack.md`
- `.conductor/tracks/**`

---

## Notes

- Conductor is opt-in: integrations only activate when you explicitly request Conductor behavior.
- Directories like `.conductor/tracks/` and `.conductor/archive/` are created on install (no `.gitkeep` files needed).
- Warp's global loader rule is manual and must be re-copied if the template changes.
