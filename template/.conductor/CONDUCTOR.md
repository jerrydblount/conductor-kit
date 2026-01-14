# Conductor Master Rule

## 1. Trigger Condition
**OPT-IN ONLY:** This rule applies ONLY when the user explicitly:
- Asks to "Start a new track"
- Asks to "Use Conductor" / "Create conductor track"
- Asks to "Update plan" / "Update the plan"
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

### Phase 1.5: Canonical Plan (Required)
Each track MUST have a single canonical plan source of truth.

Conductor supports two canonical plan sources:
- `warp_notebook`: a Warp Drive notebook URL/ID
- `local_plan_markdown`: a repo-local markdown file (recommended default: `.conductor/tracks/<track_id>/canonical_plan.md`)

Conductor track artifacts grounded in the canonical plan:
- `.conductor/tracks/<track_id>/spec.md`
- `.conductor/tracks/<track_id>/plan.md`

Rules
- The Conductor artifacts must be a faithful, executable elaboration of the canonical plan (what/why/how).
- If there is a conflict between the canonical plan and Conductor artifacts, STOP and reconcile. The canonical plan wins.
- Each track MUST record its canonical plan source in `.conductor/tracks/<track_id>/metadata.json`:
  - `canonical_plan_source`: `warp_notebook` | `local_plan_markdown`
  - If `warp_notebook`:
    - `canonical_warp_plan_url`
    - `canonical_warp_notebook_id`
  - If `local_plan_markdown`:
    - `canonical_local_plan_path` (e.g., `.conductor/tracks/<track_id>/canonical_plan.md`)
- Each track MUST maintain diffable snapshots of the canonical plan:
  - `.conductor/tracks/<track_id>/canonical_plan_snapshot.md`
  - `.conductor/tracks/<track_id>/canonical_plan_snapshots/`
  - `.conductor/tracks/<track_id>/canonical_plan_diffs/`
  - Reference: `PLAN_AUTOMATION.md`.
- Backward compatibility: older tracks may use `warp_plan_snapshot.md` / `warp_plan_snapshots/` / `warp_plan_diffs/`. Tooling should support both naming schemes.

### Phase 1.6: Token + Cost Estimation (Plan Budgeting)
When generating or updating `.conductor/tracks/<track_id>/plan.md`, you MUST include a **Token & Cost Estimate (Generated)** section near the top of the GENERATED block.

Inputs
- Estimator defaults (for raw token estimates): `.conductor/llm_estimator_defaults.json`
- Pricing (required for USD estimates): `.conductor/llm_pricing.json`
- Calibration samples (optional): `.conductor/llm_usage_samples.jsonl`
  - One JSON object per line (blank lines allowed).

Rules
- Raw token estimates must always be produced.
- USD estimates must be **blocked** (but raw tokens still shown) if pricing is missing or does not include the requested provider/model.
- Cache-aware USD must always include a scenario range at cache_hit_rate = **0.0 / 0.5 / 1.0**.
- If `.conductor/llm_usage_samples.jsonl` contains usable samples, prefer calibrated per-provider/model medians (and optionally 25/75th percentiles) when updating `.conductor/llm_estimator_defaults.json`.
- Do not overwrite LOCAL OVERRIDES when inserting/updating the estimate.

### Phase 2: Track Management

#### A. Starting a New Track
1.  **Create Directory:** `.conductor/tracks/<track_id>/` (Format: `feature_name_YYYYMMDD`)
2.  **Canonical Plan (Required):** Ask the user which canonical plan source to use:
    - If `warp_notebook`: ask for the canonical Warp Drive notebook URL.
      - Store it in `.conductor/tracks/<track_id>/metadata.json` under `canonical_warp_plan_url`.
      - Derive and store the notebook id under `canonical_warp_notebook_id`.
      - Include the URL at the top of both `spec.md` and `plan.md`.
    - If `local_plan_markdown`:
      - Create `.conductor/tracks/<track_id>/canonical_plan.md` (or use a user-provided path) and ask the user to provide the canonical plan content.
      - Store the path in `metadata.json` under `canonical_local_plan_path`.
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
    - Add / update the **Token & Cost Estimate (Generated)** section (see Phase 1.6).
    - **CRITICAL:** Inject a **Phase Checkpoint Task** at the end of each Phase (See Workflow).
    - **CRITICAL:** Phase 0 MUST include a “Canonical plan parity” task template (See Workflow).

#### B. Implementing a Track
1.  **Read Context:** Read `spec.md` and `plan.md` for the track.
2.  **Follow Workflow:** Adhere strictly to `.conductor/workflow.md`.
    -   **TDD:** Red -> Green -> Refactor.
    -   **Checkpoints:** Stop at Phase Checkpoints for manual verification.
3.  **Update Plan:** Mark tasks as `[~]` (In Progress) and `[x]` (Done) with commit hashes.

#### C. Updating a Track from the Canonical Plan ("update plan")
When the user asks to "update plan", you MUST:
1. Read `.conductor/tracks/<track_id>/metadata.json` to identify:
   - `canonical_plan_source`
   - canonical pointer fields (`canonical_warp_plan_url` / `canonical_warp_notebook_id` OR `canonical_local_plan_path`)
2. Sync the canonical plan into the track snapshot:
   - Update `.conductor/tracks/<track_id>/canonical_plan_snapshot.md`
   - Write a timestamped snapshot to `canonical_plan_snapshots/`
   - Write a timestamped diff to `canonical_plan_diffs/`
3. Regenerate Conductor artifacts:
   - Overwrite only the GENERATED blocks in `spec.md` and `plan.md`
   - Recompute and update the **Token & Cost Estimate (Generated)** section in `plan.md` (see Phase 1.6)
   - Preserve LOCAL OVERRIDES blocks byte-for-byte
4. Update `metadata.json` with snapshot hashes/timestamps and `last_sync_status`.

Constraints
- Do not modify application code during "update plan".
- If the canonical plan cannot be accessed at update time, STOP and report what is missing.
- Reference: `PLAN_AUTOMATION.md`.

### Phase 3: Finalization
1.  **Sync Documentation:** Upon track completion, review `product.md` and `tech-stack.md`. Propose updates if the track changed the product scope or introduced new tech.
2.  **Archive:** Offer to move the track to `.conductor/archive/`.
