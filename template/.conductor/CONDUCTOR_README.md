# Conductor

Conductor is a context-driven development framework implemented as repo-local artifacts (the `.conductor/` directory) plus optional IDE integrations. It enforces a strict **Context → Spec → Plan → Implement** workflow to ensure high-quality, documented, and test-driven changes.

## How to Use Conductor

### 1) Opt-In
Conductor is opt-in. The agent will only enforce the Conductor workflow when you explicitly ask for it.
- Trigger phrases include: "Start a new track", "Use Conductor", "Create conductor track", "Update plan", "Execute plan".

### 2) The Workflow

#### Step 1: Start a Track
To begin a new feature or bug fix, ask:
> "Start a new track for [Feature Name]"

The agent will:
1. Create a new directory in `.conductor/tracks/<track_id>/`.
2. Ask you to choose a canonical plan source (`warp_notebook` or `local_plan_markdown`).
3. Interview you to gather requirements.
4. Generate a `spec.md`.

#### Step 2: Plan
Once the `spec.md` is approved, the agent will:
1. Generate a `plan.md` based on the spec and canonical plan.
2. Break down the work into phases and tasks.
3. Inject phase checkpoints for manual verification.

#### Step 3: Implement
Ask the agent:
> "Implement track <track_id>"

The agent will:
1. Follow the Red → Green → Refactor TDD cycle defined in `workflow.md`.
2. Update `plan.md` statuses as it progresses.
3. Stop at phase checkpoints to guide you through manual verification.

#### Step 4: Finalize
When the track is complete:
1. The agent may propose updates to `product.md` and `tech-stack.md`.
2. The track can be archived.

## Directory Structure

- `.conductor/`
  - `product.md`: Product vision and goals (project-owned).
  - `tech-stack.md`: Technology stack and constraints (project-owned).
  - `workflow.md`: Development protocols (TDD, checkpoints, commits).
  - `tracks/`: Active and completed tracks.
    - `<track_id>/`
      - `spec.md`: Requirements.
      - `plan.md`: Implementation plan.
      - `metadata.json`: Status tracking.
      - `canonical_plan_snapshot.md`: Latest snapshot of the canonical plan.
      - `canonical_plan_snapshots/`: Archived snapshots.
      - `canonical_plan_diffs/`: Archived diffs.

## Key Files
- `CONDUCTOR.md`: The master Conductor rule file.
- `workflow.md`: The implementation workflow (TDD + checkpoints).
- `PLAN_AUTOMATION.md`: Snapshot/diff workflow + `update plan` behavior.
