# Conductor Master Rule

## 1. Trigger Condition
**OPT-IN ONLY:** This rule applies ONLY when the user explicitly:
- Asks to "Start a new track"
- Asks to "Use Conductor" / "Create conductor track"
- Asks to "Update plan" / "Update the plan"
- Asks to "Scan plan" / "Scan the plan"
- Asks to "Save scan report"
- Asks to "Execute plan" / "Execute the plan" / "Implement the plan"
- References a specific Conductor artifact (e.g., "Check the spec for track X")

If none of these conditions are met, proceed with normal agent behavior.

## 2. Core Protocol: Context-Driven Development

When the Trigger Condition is met, you MUST follow this strictly:

### Phase 1: Context Loading
Before planning or implementing, you MUST read:
- `.conductor/product.md`
- `.conductor/tech-stack.md`
- `.conductor/workflow.md`

### Phase 1.2: Conductor Memory (Required)
When Conductor is triggered, Conductor Memory is enabled.

Goals
- Persist a **lossless transcript** of the user↔agent conversation.
- Persist tool activity (tool calls + tool results).

Canonical store (per track)
- `.conductor/tracks/<track_id>/memory/transcript.jsonl` (append-only)
- `.conductor/tracks/<track_id>/memory/state.json`

Hard requirements
- **Fail closed:** If a memory append fails (cannot persist locally), you MUST STOP and report the error.
  - You MUST offer an explicit override: the user can tell you to continue by saying: "continue without memory".
- You MUST append these event types:
  - `message`: for every user and assistant message
  - `tool_call`: before each tool invocation
  - `tool_result`: after each tool completes
  - `artifact`: when large tool output or other blobs are stored as files

Journaler (preferred, Tier 2)
- Use the CLI journaler:
  - `conductor memory append --track-id <track_id> --event-file -`
  - Use `--event-file -` and pass JSON via stdin.

Fallback (Tier 1)
- If the CLI is not available or cannot run, you may append directly to the track transcript JSONL.

Non-blocking summary
- You MAY run `conductor memory summarize --track-id <track_id>` to update `summary.md`.
- Summary generation must be non-blocking: failures must not prevent continuing work once canonical transcript persistence is satisfied.

### Phase 1.5: Canonical Plan (Required)
Each track MUST have a single canonical plan source of truth.

Conductor supports one canonical plan source:
- `local_plan_markdown`: a repo-local markdown file (recommended default: `.conductor/tracks/<track_id>/canonical_plan.md`)

Conductor track artifacts grounded in the canonical plan:
- `.conductor/tracks/<track_id>/spec.md`
- `.conductor/tracks/<track_id>/plan.md`

Rules
- The Conductor artifacts must be a faithful, executable elaboration of the canonical plan (what/why/how).
- If there is a conflict between the canonical plan and Conductor artifacts, STOP and reconcile. The canonical plan wins.
- Each track MUST record its canonical plan source in `.conductor/tracks/<track_id>/metadata.json`:
  - `canonical_plan_source`: `local_plan_markdown`
  - `canonical_local_plan_path` (e.g., `.conductor/tracks/<track_id>/canonical_plan.md`)
- Each track MUST maintain diffable snapshots of the canonical plan:
- `.conductor/tracks/<track_id>/canonical_plan_snapshot.md`
- `.conductor/tracks/<track_id>/canonical_plan_snapshots/`
- `.conductor/tracks/<track_id>/canonical_plan_diffs/`
- Reference: `PLAN_AUTOMATION.md`.
- Backward compatibility: older tracks may use `warp_plan_snapshot.md` / `warp_plan_snapshots/` / `warp_plan_diffs/`. Tooling should support both naming schemes.

### Phase 2: Track Management

#### A. Starting a New Track
1.  **Create Directory:** `.conductor/tracks/<track_id>/` (Format: `feature_name_YYYYMMDD`)
2.  **Canonical Plan (Required):** Create `.conductor/tracks/<track_id>/canonical_plan.md` (or use a user-provided path) and ask the user to provide the canonical plan content.
    - Store the path in `metadata.json` under `canonical_local_plan_path` and set `canonical_plan_source` to `local_plan_markdown`.
    - Include a reference to the canonical plan at the top of `spec.md` and `plan.md`.
    - Initialize plan automation artifacts:
      - `canonical_plan_snapshot.md`
      - `canonical_plan_snapshots/`
      - `canonical_plan_diffs/`
      - Ensure `spec.md` / `plan.md` have GENERATED + LOCAL OVERRIDES blocks.
    - Reference: `PLAN_AUTOMATION.md`.
3.  **Interview Protocol:** You MUST ask the user the following questions sequentially to build `spec.md`. Do not assume answers.
    -   **Goal:** "What is the primary user-facing goal of this feature or bug fix?"
    -   **Functional Requirements:** "What specific actions must the user be able to perform? What are the inputs and outputs?"
    -   **Non-Functional Requirements:** "Are there constraints on performance, security, or supported platforms?"
    -   **Out of Scope:** "What are we explicitly *not* building in this track?"
    -   **Acceptance Criteria:** "How will we verify that this feature is complete?"
4.  **Generate Spec:** Write the answers into `.conductor/tracks/<track_id>/spec.md`.
5.  **Generate Plan:** create `.conductor/tracks/<track_id>/plan.md`.
    - Break down into **Phases** and **Tasks**.
    - **CRITICAL:** Inject a **Phase Checkpoint Task** at the end of each Phase (See Workflow).
    - **CRITICAL:** Phase 0 MUST include a “Canonical plan parity” task template (See Workflow).

#### B. Implementing a Track
1.  **Read Context:** Read `spec.md` and `plan.md` for the track.
2.  **Recommend Plan Scan (Recommended):** Offer to run "scan plan" first to catch contradictions, conflicts, and gaps before implementation. If the user declines, proceed.
3.  **Follow Workflow:** Adhere strictly to `.conductor/workflow.md`.
    -   **TDD:** Red -> Green -> Refactor.
    -   **Checkpoints:** Stop at Phase Checkpoints for manual verification.
4.  **Update Plan:** Mark tasks as `[~]` (In Progress) and `[x]` (Done) with commit hashes.

#### C. Updating a Track from the Canonical Plan ("update plan")
When the user asks to "update plan", you MUST:
1. Read `.conductor/tracks/<track_id>/metadata.json` to identify:
   - `canonical_plan_source`
   - `canonical_local_plan_path`
2. Sync the canonical plan into the track snapshot:
   - Update `.conductor/tracks/<track_id>/canonical_plan_snapshot.md`
   - Write a timestamped snapshot to `canonical_plan_snapshots/`
   - Write a timestamped diff to `canonical_plan_diffs/`
3. Regenerate Conductor artifacts:
   - Overwrite only the GENERATED blocks in `spec.md` and `plan.md`
   - Preserve LOCAL OVERRIDES blocks byte-for-byte
4. Update `metadata.json` with snapshot hashes/timestamps and `last_sync_status`.

Constraints
- Do not modify application code during "update plan".
- If the canonical plan cannot be accessed at update time, STOP and report what is missing.
- Reference: `PLAN_AUTOMATION.md`.

#### D. Scanning a Plan ("scan plan")
When the user asks to "scan plan" (or "scan the plan"), you MUST perform a deep, read-only review and produce a scan report.

Inputs to read (minimum)
- `.conductor/product.md`
- `.conductor/tech-stack.md`
- `.conductor/workflow.md`
- `.conductor/tracks/<track_id>/metadata.json`
- `.conductor/tracks/<track_id>/spec.md` (if present)
- `.conductor/tracks/<track_id>/plan.md` (if present)
- Canonical plan markdown (required for cross-checks)
  - Prefer: the repo-local file at the path in `metadata.json` -> `canonical_local_plan_path`
  - Also read (if present): `.conductor/tracks/<track_id>/canonical_plan_snapshot.md` and call out any drift vs the canonical plan file

Hard stop / required clarifications
- If `track_id` is not specified and cannot be inferred unambiguously, ask which track to scan.
- If the canonical plan markdown cannot be read (missing path, missing file, or inaccessible), the scan report MUST include this as a BLOCKER and ask the user what the canonical plan path should be (or instruct to run "update plan" if appropriate).

Scan checks (minimum)
1) Conflicts between phases and tasks
- Task ordering issues (prerequisites missing, outputs referenced before produced)
- Duplicate tasks that conflict in intent, scope, or expected outputs
- Phase boundary issues (work that belongs in earlier phases is scheduled later; missing checkpoints)

2) Contradictions in requirements
- Canonical plan vs spec vs plan mismatches
- Internal contradictions within the canonical plan, within spec, or within plan

3) Gaps in requirements and coverage
- Acceptance criteria not covered by tasks/tests
- Missing non-functional work implied by requirements (performance, security, migrations, observability, rollout/rollback)
- Missing verification steps or definition-of-done tasks required by `.conductor/workflow.md`

4) Agent understanding gaps
- Flag ambiguous or underspecified requirements, unclear user flows, unclear inputs/outputs, or missing context.
- Ask targeted clarification questions when ambiguity blocks a confident scan.

Output requirements
- Produce a structured "Plan Scan Report" in chat.
- Group findings by severity: BLOCKER / WARNING / SUGGESTION.
- Each finding MUST include: what is wrong, why it matters, and a concrete recommendation (typically plan/spec edits).
- Include a "Questions for you" section when clarification is required.
- The scan MUST NOT modify files by default.

Optional saving ("save scan report")
- If the user asks to "save scan report" (either as a follow-up or in the same message), write the report to:
  - `.conductor/tracks/<track_id>/plan_scans/<YYYYMMDD_HHMMSSZ>.md`
- If no scan report has been produced in the current run, perform the scan first, then save.

### Phase 3: Finalization
1.  **Sync Documentation:** Upon track completion, review `product.md` and `tech-stack.md`. Propose updates if the track changed the product scope or introduced new tech.
2.  **Archive:** Offer to move the track to `.conductor/archive/`.
