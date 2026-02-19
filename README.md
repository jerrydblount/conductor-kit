# Conductor Kit

Conductor Kit is an IDE-agnostic, repo-local toolkit for context-driven agentic development.

## What is Conductor Kit
Conductor Kit is a repo-local, IDE-agnostic way to run context-driven development:
- You keep the workflow, product context, and tech constraints in the repo under `.conductor/`.
- Work is organized into **tracks** (`.conductor/tracks/<track-name>/`) with a `spec.md`, `plan.md`, and `metadata.json`.
- Plans are captured in a **canonical plan** format (repo-local markdown) and converted into Conductor tracks.
- The system produces durable artifacts (snapshots and diffs) so work is auditable and repeatable.

Conductor Kit is a port of the Gemini CLI [Conductor](https://github.com/gemini-cli-extensions/conductor) extension. It's not a 1:1 copy; modifications have been made and additional features added. The original Conductor extension was built for Gemini CLI only. Conductor Kit takes the same approach and makes it available to Warp, Cursor, and any IDE that supports agent rules files (`AGENTS.md`, `.cursorrules`, or similar).

The original Conductor introduced a simple idea: store your product context, tech stack constraints, and workflow preferences in the repo alongside your code. When your AI assistant starts a task, it reads those files first. Work is organized into tracks (isolated directories for each feature or bug fix) with specs, plans, and implementation checkpoints. The result is that your AI assistant follows a consistent protocol instead of starting fresh every session.

Conductor Kit packages this into a template that gets installed into any repo, a CLI to manage installations, and integration files for different IDEs.

## Who is this for

- **Solopreneurs**: You're building alone with an AI assistant. Conductor Kit keeps your product context and tech decisions in files that persist across sessions, so your assistant doesn't lose track of what you're building or how.
- **Startups**: Multiple people (or multiple agents) work in the same codebase. The shared context files in `.conductor/` give everyone the same starting point. New team members can read `product.md` and `tech-stack.md` to get oriented.
- **Small tech companies**: You have an established product and you're adding features. The track/plan/spec workflow gives you a structured way to define work before implementation starts, and phase checkpoints let you verify along the way.
- **Enterprise product teams**: You need auditable, repeatable workflows. Track artifacts (plan snapshots, diffs, scan reports, memory transcripts) provide a paper trail for every piece of AI-assisted work.

## Features

- **Context-driven development**: Product goals, tech stack constraints, and workflow preferences live in `.conductor/` as markdown files. Your AI assistant reads them before every interaction, so it works with your project's actual constraints instead of guessing.

- **Tracks**: Each feature or bug fix gets its own directory (`.conductor/tracks/<track_id>/`) with a spec, plan, and metadata file. Tracks keep units of work isolated and make progress visible through task status markers.

- **Interview-based specs**: When you start a track, Conductor walks through a structured interview: goal, functional requirements, non-functional requirements, out-of-scope items, and acceptance criteria. The answers are written into a `spec.md` file.

- **Plan generation and phases**: Plans break work into phases and tasks. Each phase ends with a checkpoint where the agent stops and waits for you to verify before continuing.

- **Canonical plan sync**: Plans are grounded in a canonical markdown file. When the canonical plan changes, running "update plan" regenerates the spec and plan while preserving any local overrides you've added. Snapshots and diffs are stored for every sync.

- **Plan scanning**: Before implementation, a read-only scan cross-checks the canonical plan against the spec and plan. It flags conflicts, contradictions, gaps, and ambiguities, grouped by severity: blocker, warning, or suggestion.

- **TDD workflow**: Implementation follows a Red → Green → Refactor cycle defined in `workflow.md`. The agent writes failing tests first, implements just enough to pass, then refactors.

- **Conductor Memory**: Every track records a lossless conversation transcript as append-only JSONL. An optional local Postgres database with full-text search can index transcripts for retrieval. *(The Postgres integration is experimental and has not been fully tested. The JSONL transcript works without it.)*

- **IDE integrations**: Ships with integration templates for Warp (global loader rule), Cursor (`.cursorrules`), and any tool that reads `AGENTS.md`.

- **CLI**: `bin/conductor` handles `init`, `upgrade`, `version`, `doctor`, `integrate`, and `memory` commands. All commands support `--dry-run` and `--yes` flags.

---

## Installation

Installing Conductor Kit is a two-part process:
1. **Part A**: Get the Conductor Kit CLI onto your machine (once).
2. **Part B**: Use the CLI to install Conductor into each project repo.

### Part A: install the CLI (once)

#### Step 1: Clone the repository

Pick a permanent location on your machine:

```sh
git clone https://github.com/jerrydblount/conductor-kit.git ~/conductor-kit
```

#### Step 2: Verify the CLI runs

```sh
python3 ~/conductor-kit/bin/conductor --help
```

You should see:

```
usage: conductor [-h] [--dry-run] [--yes] {init,upgrade,version,doctor,integrate} ...
```

### Part B: install Conductor into a project repo

Repeat these steps for each repo where you want to use Conductor.

#### Step 1: Run `conductor init`

```sh
python3 ~/conductor-kit/bin/conductor init /path/to/your-project
```

Or from inside the project root:

```sh
python3 ~/conductor-kit/bin/conductor init .
```

This creates:
- `.conductor/` directory with:
  - `CONDUCTOR.md`: the master rule that guides your AI assistant
  - `workflow.md`: the TDD and checkpoint protocol
  - `CONDUCTOR_README.md`, config files, `.gitignore`
  - `memory/`: Conductor Memory config and local DB scaffold
  - `tracks/`: where track directories will live
  - `archive/`: for completed/archived tracks
  - `product.md`: placeholder for product context (populated by the AI assistant)
  - `tech-stack.md`: placeholder for tech constraints (populated by the AI assistant)
- `PLAN_AUTOMATION.md` at the repo root

#### Step 2: Add IDE integration

Choose one:

**Warp** (global loader rule, manual setup):
1. Run `python3 ~/conductor-kit/bin/conductor integrate warp` to see the rule text.
2. Copy the output.
3. Paste it into Warp Settings → Rules.

This is a one-time step. If the template changes in future releases, you'll need to re-copy/paste.

**Cursor** (repo-local):
```sh
python3 ~/conductor-kit/bin/conductor integrate cursor /path/to/your-project
```
Creates `.cursorrules` in your project.

**Other IDEs / generic** (repo-local):
```sh
python3 ~/conductor-kit/bin/conductor integrate generic /path/to/your-project
```
Creates `AGENTS.md` in your project.

#### Step 3: Verify the installation

```sh
python3 ~/conductor-kit/bin/conductor doctor /path/to/your-project
```

You should see `OK` for all required files.

```sh
python3 ~/conductor-kit/bin/conductor version /path/to/your-project
```

Prints the installed Conductor version.

---

## Usage

Conductor is opt-in. It only activates when you explicitly trigger it.

### Trigger phrases

Your AI assistant will engage Conductor when you say:
- "Start a new track" / "Create conductor track"
- "Use Conductor"
- "Update plan" / "Update the plan"
- "Scan plan" / "Scan the plan"
- "Save scan report"
- "Execute plan" / "Execute the plan" / "Implement the plan"
- Or reference a Conductor artifact (e.g., "Check the spec for track X")

If you don't use a trigger phrase, the assistant behaves normally.

### The workflow

#### 1. Start a track

Say: "Start a new track for [Feature Name]"

The assistant will:
1. Create a track directory (`.conductor/tracks/<track_id>/`)
2. Ask you for the canonical plan markdown file (default: `.conductor/tracks/<track_id>/canonical_plan.md`) and the canonical plan content
3. Interview you to gather requirements (goal, functional/non-functional requirements, out of scope, acceptance criteria)
4. Generate `spec.md`

#### 2. Plan

Once the spec is ready, the assistant will:
1. Generate `plan.md` based on the spec and canonical plan
2. Break work into phases and tasks
3. Add phase checkpoints for manual verification

#### 3. Scan (recommended)

Before implementation, say: "Scan plan"

The assistant will cross-check the canonical plan against the spec and plan, then produce a scan report with findings grouped by severity (blocker / warning / suggestion). To save the report to the repo, say: "Save scan report".

#### 4. Implement

Say: "Execute the plan" or "Implement track \<track_id\>"

The assistant will:
1. Follow the TDD workflow (Red → Green → Refactor) from `workflow.md`
2. Update task statuses in `plan.md` as it works (`[ ]` → `[~]` → `[x]`)
3. Stop at phase checkpoints for your verification

#### 5. Finalize

When the track is complete:
1. The assistant may propose updates to `product.md` and `tech-stack.md` if the track changed the product scope or introduced new tech
2. The track can be archived to `.conductor/archive/`

### Updating a plan

If you change the canonical plan markdown file, say: "Update the plan"

The assistant will sync the canonical plan into the track, regenerate `spec.md` and `plan.md` (preserving local overrides), and store a snapshot and diff.

### Scanning a plan (recommended)

Before implementation, say: "Scan plan"

The assistant will cross-check the canonical plan markdown against the track `spec.md` and `plan.md`, then produce a structured scan report highlighting conflicts, contradictions, gaps, and clarification questions.

To save the report to the repo (optional), say: "Save scan report".

---


## Upgrading

To upgrade Conductor-managed files in an existing repo:

```sh
python3 ~/conductor-kit/bin/conductor upgrade /path/to/your-project
```

By default, this:
- Updates Conductor-managed files (CONDUCTOR.md, CONDUCTOR_README.md, workflow.md, PLAN_AUTOMATION.md)
- Does NOT overwrite `.conductor/product.md` or `.conductor/tech-stack.md`
- Never touches `.conductor/tracks/**`

To overwrite project-owned context files (shows diff, backs up, asks for confirmation):

```sh
python3 ~/conductor-kit/bin/conductor upgrade /path/to/your-project --overwrite-product
python3 ~/conductor-kit/bin/conductor upgrade /path/to/your-project --overwrite-techstack
```

For major version upgrades with breaking changes:

```sh
python3 ~/conductor-kit/bin/conductor upgrade /path/to/your-project --accept-breaking
```

See `CHANGELOG.md` and `UPGRADING.md` for details.

---

## CLI reference

- `conductor init [path]`: Install Conductor into a repo
- `conductor upgrade [path]`: Upgrade Conductor-managed files
- `conductor version [path]`: Print installed version
- `conductor doctor [path]`: Check installation health
- `conductor integrate {warp,cursor,generic} [path]`: Install IDE integration
- `conductor memory append`: Append an event to a track's transcript
- `conductor memory summarize`: Generate a summary of a track's transcript
- `conductor memory backfill-db`: Backfill transcript events into the local Postgres database
- `conductor memory db {up,down,status,migrate,psql}`: Manage the local Postgres database

All commands accept `--dry-run` (print actions without writing) and `--yes` (auto-confirm prompts).

---

## Project status

Conductor Kit is early. The current version is 0.3.0. The core workflow (context loading, track creation, spec/plan generation, plan scanning, and TDD implementation) works. Some features are still in progress:

- The Postgres database for Conductor Memory is experimental and has not been fully tested. The JSONL transcript (which does not require Postgres) works.

If you run into problems or have ideas, open an issue on [GitHub](https://github.com/jerrydblount/conductor-kit/issues). Contributions are welcome; see `CHANGELOG.md` for what's changed so far.

---

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for the full text.
