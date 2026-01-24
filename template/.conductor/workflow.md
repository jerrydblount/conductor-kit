# Project Workflow

## Guiding Principles

1. **The Canonical Plan is Canonical:** The track’s canonical plan source (repo-local markdown) is the source of truth for Conductor `spec.md` + `plan.md`. If there is any conflict, STOP and reconcile. The canonical plan wins.
2. **Conductor Artifacts are Generated:** `spec.md` and `plan.md` are treated as generated outputs from the canonical plan snapshot, except for explicit LOCAL OVERRIDES blocks.
3. **The Plan is the Source of Truth:** All work must be tracked in `plan.md`
4. **The Tech Stack is Deliberate:** Changes to the tech stack must be documented in `tech-stack.md` *before* implementation
5. **Test-Driven Development:** Write unit tests before implementing functionality
6. **High Code Coverage:** Aim for >80% code coverage for all modules
7. **User Experience First:** Every decision should prioritize user experience
8. **Non-Interactive & CI-Aware:** Prefer non-interactive commands. Use `CI=true` for watch-mode tools (tests, linters) to ensure single execution.

Reference
- See `PLAN_AUTOMATION.md` for the supported user commands and the snapshot/diff workflow.

## Phase 0 Required Tasks (Template)
Every track MUST include Phase 0 tasks that ensure the Conductor artifacts are a faithful, executable elaboration of the canonical plan.

Required Phase 0 tasks
- Canonical plan linkage
  - Ensure `.conductor/tracks/<track_id>/metadata.json` contains:
    - `canonical_plan_source`: `local_plan_markdown`
    - `canonical_local_plan_path`
  - Ensure `spec.md` and `plan.md` include a reference to the canonical plan near the top.
- Snapshot + diff tracking (required)
  - Generate/refresh `.conductor/tracks/<track_id>/canonical_plan_snapshot.md` from the canonical plan source.
  - Archive a timestamped snapshot under `canonical_plan_snapshots/`.
  - Write a diff file under `canonical_plan_diffs/` comparing the prior snapshot to the new snapshot.
  - Update metadata with snapshot sha256 + generated_at.
- Generated vs overrides (required)
  - Ensure `spec.md` and `plan.md` contain:
    - `<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->`
    - `<!-- BEGIN LOCAL OVERRIDES -->` / `<!-- END LOCAL OVERRIDES -->`
  - Preserve LOCAL OVERRIDES byte-for-byte on every `update plan`.
- Canonical plan parity (contract)
  - Confirm the Conductor `spec.md` fully covers the canonical plan (what).
  - Confirm the Conductor `plan.md` fully covers the canonical plan (why/how) and is executable (phases/tasks/checkpoints/tests).
  - If any mismatch is found, STOP and reconcile before implementation.

## Task Workflow

All tasks follow a strict lifecycle:

### Standard Task Workflow

1. **Select Task:** Choose the next available task from `plan.md` in sequential order

2. **Mark In Progress:** Before beginning work, edit `plan.md` and change the task from `[ ]` to `[~]`

3. **Write Failing Tests (Red Phase):**
   - Create a new test file for the feature or bug fix.
   - Write one or more unit tests that clearly define the expected behavior and acceptance criteria for the task.
   - **CRITICAL:** Run the tests and confirm that they fail as expected. This is the "Red" phase of TDD. Do not proceed until you have failing tests.

4. **Implement to Pass Tests (Green Phase):**
   - Write the minimum amount of application code necessary to make the failing tests pass.
   - Run the test suite again and confirm that all tests now pass. This is the "Green" phase.

5. **Refactor (Optional but Recommended):**
   - With the safety of passing tests, refactor the implementation code and the test code to improve clarity, remove duplication, and enhance performance without changing the external behavior.
   - Rerun tests to ensure they still pass after refactoring.

6. **Verify Coverage:** Run coverage reports using the project's chosen tools.
   Target: >80% coverage for new code.

7. **Document Deviations:** If implementation differs from tech stack:
   - **STOP** implementation
   - Update `tech-stack.md` with new design
   - Add dated note explaining the change
   - Resume implementation

8. **Commit Code Changes:**
   - Stage all code changes related to the task.
   - Propose a clear, concise commit message e.g, `feat(ui): Create basic HTML structure for calculator`.
   - Perform the commit.

9. **Update Plan with Commit Hash:**
    - Read `plan.md`, find the line for the completed task, update its status from `[~]` to `[x]`, and append the first 7 characters of the *just-completed commit's* commit hash.
    - Write the updated content back to `plan.md`.

### Phase Completion Verification and Checkpointing Protocol

**Trigger:** This protocol is executed immediately after a task is completed that also concludes a phase in `plan.md`.

1.  **Announce Protocol Start:** Inform the user that the phase is complete and the verification and checkpointing protocol has begun.

2.  **Ensure Test Coverage for Phase Changes:**
    -   **Determine Phase Scope:** Identify files changed in this phase.
    -   **Verify and Create Tests:** Ensure all changed code files have corresponding tests.

3.  **Execute Automated Tests:**
    -   Announce and run the test suite.
    -   If tests fail, debug (max 2 attempts) or report failure.

4.  **Propose Manual Verification Plan:**
    -   Generate a step-by-step manual verification plan for the user based on `product.md` and the completed phase.
    -   Present this plan to the user.

5.  **Await Explicit User Feedback:**
    -   Ask: "**Does this meet your expectations? Please confirm with yes or provide feedback.**"
    -   **PAUSE** and await the user's response.

6.  **Create Checkpoint Commit:**
    -   Stage all changes.
    -   Commit with message: `conductor(checkpoint): Checkpoint end of Phase X`.

7.  **Update Plan with Checkpoint:**
    -   Update `plan.md` with `[checkpoint: <sha>]` for the completed phase.

8.  **Announce Completion:** Inform the user that the phase is complete.

### Quality Gates

Before marking any task complete, verify:

- [ ] All tests pass
- [ ] Code coverage meets requirements (>80%)
- [ ] Code follows project's code style guidelines
- [ ] All public functions/methods are documented
- [ ] Type safety is enforced
- [ ] No linting or static analysis errors
- [ ] Works correctly on mobile (if applicable)
- [ ] Documentation updated if needed
- [ ] No security vulnerabilities introduced

## Commit Guidelines

### Message Format
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests
- `chore`: Maintenance tasks
