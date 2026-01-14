# AI Assistant Instructions (Conductor)

## Opt-in only
Use Conductor ONLY when the user explicitly asks to:
- "Start a new track"
- "Use Conductor" / "Create conductor track"
- "Update plan" / "Update the plan"
- "Execute plan" / "Execute the plan" / "Implement the plan"
- or references Conductor artifacts (e.g., a specific track `spec.md` / `plan.md`).

If the user does not opt in, behave normally.

## On Conductor opt-in
1) Verify Conductor is installed:
- If `.conductor/CONDUCTOR.md` does not exist, tell the user Conductor is not installed in this repo and instruct them to install it via `conductor init`.
- If it exists, continue.

2) Load required context (must read before planning/implementation):
- `.conductor/product.md`
- `.conductor/tech-stack.md`
- `.conductor/workflow.md`
- `.conductor/CONDUCTOR.md`

3) Follow the protocol:
- Treat `.conductor/CONDUCTOR.md` as the authoritative Conductor protocol for this repo.
- Use the canonical plan rules from `PLAN_AUTOMATION.md` for "update plan" behavior.

## Notes
- Conductor is designed to be repo-local and IDE-agnostic: the `.conductor/` directory is the source of truth.
- Track snapshots/diffs are required regardless of IDE.
