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

#### Step A3: (Recommended) Make `conductor` available as a command

Choose one of these options:

**Option 1: Shell alias (simplest)**

Add this line to your shell config file (`~/.zshrc` or `~/.bashrc`):

```sh
alias conductor="python3 ~/conductor-kit/bin/conductor"
```

Then reload:

```sh
source ~/.zshrc
```

Now you can run `conductor` from anywhere.

**Option 2: Symlink on PATH (cleaner long-term)**

```sh
mkdir -p ~/.local/bin
ln -sf ~/conductor-kit/bin/conductor ~/.local/bin/conductor
```

Make sure `~/.local/bin` is on your PATH. Add this to `~/.zshrc` if needed:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

Reload:

```sh
source ~/.zshrc
```

**Option 3: Use the full path every time (no setup)**

Just run:

```sh
python3 ~/conductor-kit/bin/conductor <command>
```

---

### Part B: Install Conductor into a project repo

Repeat these steps for each repo where you want to use Conductor.

#### Step B1: Run `conductor init`

From anywhere, run:

```sh
conductor init /path/to/your-project
```

Or, if you are already in the project root:

```sh
conductor init .
```

This creates:
- `.conductor/` directory with:
  - `CONDUCTOR.md` (the master rule that guides your AI assistant)
  - `workflow.md`, `CONDUCTOR_README.md`, config files
  - `tracks/` (where track folders will live)
  - `archive/` (used for backups)
  - `product.md` (placeholder — you fill this in)
  - `tech-stack.md` (placeholder — you fill this in)
- `PLAN_AUTOMATION.md` at the repo root

#### Step B2: Fill in project context (important!)

Open and edit these two files in your project:

**`.conductor/product.md`**
Describe your product: what it is, who it's for, goals, success criteria.

**`.conductor/tech-stack.md`**
Describe your tech stack: languages, frameworks, deployment, testing, constraints.

These files are "project-owned" — upgrades will NOT overwrite them.

#### Step B3: Add IDE integration (choose one)

**For Warp (global loader rule — manual setup)**

Warp uses a single global rule that delegates to the repo-local `.conductor/CONDUCTOR.md`.

1. Run this to see the rule text:
   ```sh
   conductor integrate warp
   ```
2. Copy the printed text.
3. Paste it into Warp's global rules (Warp Settings → Rules).

Note: This is a one-time manual step. `conductor init` / `conductor upgrade` cannot modify Warp's global rules. If the template changes in future releases, you must re-copy/paste.

**For Cursor (repo-local)**

```sh
conductor integrate cursor /path/to/your-project
```

This creates `.cursorrules` in your project.

**For other IDEs / generic (repo-local)**

```sh
conductor integrate generic /path/to/your-project
```

This creates `AGENTS.md` in your project.

#### Step B4: Verify the installation

```sh
conductor doctor /path/to/your-project
```

You should see `OK` for all required files and directories.

```sh
conductor version /path/to/your-project
```

Shows the installed Conductor version.

---

## Quick Start Checklist

If you want the minimal steps:

```sh
# 1. Clone conductor-kit (once)
git clone https://github.com/jerrydblount/conductor-kit.git ~/conductor-kit

# 2. Add alias (once)
echo 'alias conductor="python3 ~/conductor-kit/bin/conductor"' >> ~/.zshrc
source ~/.zshrc

# 3. Init a project
conductor init /path/to/your-project

# 4. Edit product + tech-stack context
# (open .conductor/product.md and .conductor/tech-stack.md in your editor)

# 5. Add IDE integration (pick one)
conductor integrate warp          # prints text for Warp global rule
conductor integrate cursor /path/to/your-project
conductor integrate generic /path/to/your-project

# 6. Verify
conductor doctor /path/to/your-project
```

---

## Usage

Conductor is opt-in. It only activates when you explicitly ask.

In your IDE, say things like:
- "Use Conductor. Start a new track: payments-refactor"
- "Use Conductor. Update the plan for track payments-refactor"
- "Use Conductor. Execute the plan"

The assistant will read `.conductor/CONDUCTOR.md` and follow its rules.

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
