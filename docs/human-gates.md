# Human gates — what each one is actually asking of you

Organized per gate, so you can jump straight to the one that's open rather than reading the whole file. Each entry: what decision it wants, what to read first, what each move commits to.

---

## Concept gate (standard-triage features only)

**Reads:** `concept.md` alongside `context.md`.
**Moves:**
- **Approve** → architecture designer and critic start.
- **Revise** → your feedback goes back to the concept writer.
- **Reject** → the feature stops here. Cheapest point to stop something that shouldn't be built.

## Architecture gate (standard-triage features only)

**Reads:** the proposal alongside the *full* critique history — not just the latest round.
**Moves:**
- **Approve** → the ADR maker formalizes the accepted decisions.
- **Revise** → feedback to the designer, alongside what the critic already flagged.
- **Reject** → back to concept, or abandon.

## Spec gate

**Reads:** the clarified `spec.md` — worth reading in full, not skimming a summary. Clarify has already run automatically before this gate opened.
**Moves:**
- **Approve** → plan.
- **Revise** → specify (and clarify again if new ambiguity appears) re-runs with your feedback folded in.

## Plan gate

**Reads:** `plan.md` plus anything `/speckit.analyze` flagged as inconsistent.
**Moves:**
- **Approve** → fan-out to worker panes begins.
- **Revise** → back to plan.

## Checkpoint gate (once per user-story phase)

**Reads:** the phase's result — worker diffs merged, tests passing.
**Moves:**
- **Approve, not final phase** → next phase's tasks open.
- **Approve, final phase** → moves to review.
- **Revise** → specific worker panes respawn with your feedback.

## Review gate

**Reads:** the code reviewer's report — findings by severity, against spec intent and constitution compliance, not just "tests pass."
**Moves (only two — no revise-in-place):**
- **Approve** → verification.
- **Restart** → the review report carries forward, and the *entire cycle* restarts from triage, not just from spec. This is expensive by design — a review-level problem usually traces upstream of the code itself.

## Verification gate

**Reads:** the verification report, per story — pass, or fail with full diagnosis and mitigation history. Only reaches you after every story passes, or two mitigation rounds fail on the same story.
**Moves (only two — no revise):**
- **Approve** → docs.
- **Reject** → the feature stops here, reviewed but not verified — you handle it directly from here.

## Docs gate

**Reads:** the doc updates.
**Moves:**
- **Approve** → PR proposal.
- **Revise** → back to techwriter.
- **Reject** → stop; code and docs remain as artifacts, no PR opened.

## PR gate

**Reads:** the draft PR/MR description — the last thing you see before a branch is pushed and an MR opened using exactly this text, unedited after approval.
**Moves:**
- **Approve** → branch pushed, MR opened.
- **Revise** → back to the PR writer.
- **Reject** → stop; fully reviewed and documented but never proposed.
