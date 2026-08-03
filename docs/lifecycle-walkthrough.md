# Lifecycle walkthrough: empty repo to ongoing feature delivery

Condensed from `concepts/claude-only-pipeline/20260720-115709_lifecycle-walkthrough-empty-repo-to-ongoing-feature-delivery.md` — read that concept for the full transition analysis and open questions.

## Phase 0 — preconditions, once, before touching the repo

Claude Code authenticated, cmux installed and reachable, `specify` CLI installed, and the 12 role skills available in this template repository, pinned to a version.

## Phase 1 — scaffold this specific repository

The 9-step sequence in `docs/scaffolding-guide.md`, run once per repository via `scaffold.sh`.

## Phase 2 — your first real feature

Mechanically identical to every feature that follows (see Phase 3). Walk the full gate sequence in `docs/human-gates.md`. **What's actually different about feature #1 specifically**: the researcher has no prior `concept.md`, ADR, or `spec.md` in this project to draw on — `context.md` leans entirely on the raw input and external research. Expected, not a defect.

## Phase 3 — the transition to feature #2 and beyond

Starting the next feature is not a separate procedure — it's Phase 2, run again, with three concrete differences from the first run:

- **The log is shared, not restarted.** The new feature's `feature_init` entry appends to the *same* `factory-log.md` every prior feature used, tagged with its own feature identifier.
- **The researcher now has real prior art to find** — it reads this project's own accumulated concepts, ADRs, and specs before drafting `context.md`. This is the mechanism by which "the director understands previous work," even though the director's own session carries no memory of prior features.
- **Nothing else carries forward as live state.** Worktrees, panes, and task boards are feature-scoped and torn down at the end of each feature's lifecycle. What *does* carry forward automatically is the constitution itself, unchanged unless deliberately revised.

**Worth doing deliberately between features, though nothing forces it automatically**: review the dashboard's run statistics from the feature that just completed and decide whether `constitution.md` needs adjusting before the next feature starts. Nothing schedules this for you — it's a habit worth building.

## Summary: what changes and what doesn't

| Transition | What's new | What stays the same |
|---|---|---|
| Machine → first repo | This repo's git history, skill pull, project-specific constitution values | The template repository, Spec Kit, cmux, Claude Code auth |
| Scaffolded repo → first feature | `factory-log.md` gains its first real entry; researcher works from near-empty history | Every gate, role, and tier assignment |
| Feature N → feature N+1 | A new `feature_init` entry in the same log; researcher now has real prior art; possibly a revised constitution | The scaffold itself (run once, not repeated); the skills; the gate sequence |
