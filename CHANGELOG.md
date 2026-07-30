# Changelog

Bundled versioning — one tag names one consistent state of skills, dashboard, log schema, and constitution template together. See `docs/scaffolding-guide.md` for what a version pin actually covers.

## v0.1.1 — 2026-07-30

**Added:**
- `scaffold/scaffold.py` + `scaffold/scaffold.sh` — the fresh-scaffold and `--sync` paths are both implemented and tested end-to-end against a real target directory and a real authenticated clone of this repository:
  - Fresh scaffold: authenticated `gh` clone at a pinned tag, atomic copy of skills/dashboard/docs (no partial state on a failed copy), constitution + factory-log rendering (only the three mechanically-known version-pin values are substituted — every other `<<FILL:...>>` marker is left for the human), the `<<FILL:...>>` readiness gate, and a manual-steps checklist.
  - `--sync`: shows a file-level diff preview (added/removed/changed) before touching anything, prompts for confirmation, wholesale-overwrites skills/dashboard/docs, and does a structural merge on `constitution.md` (appends any new required sections as flagged placeholders, never touches the human's already-filled values). `factory-log.md` is never touched.
  - Fresh-scaffold now refuses cleanly (rather than silently overwriting) if the target already has a `constitution.md` — caught during testing: an unguarded re-run would have destroyed in-progress human edits, which is a correctness bug this version fixes before it could ship.
**Known gaps, carried forward:**
- `specify` (GitHub Spec Kit CLI) integration is best-effort: if it's not installed on the machine running the scaffold, `scaffold.sh` prints a clear warning and continues rather than failing — verified against an environment where `specify` was genuinely absent.
- Live-`cmux` verification (dashboard frontend, `/panes` response shape) is still outstanding — see v0.1.0's known gaps, unchanged.

## v0.1.0 — 2026-07-30

Initial release. All artifacts through Phase 3 of the build plan (`docs/implementation-plan.md`).

**Added:**
- `factory-log/` — schema v1 (`SCHEMA.md`), reference validator (`validator.py`), 3 fixtures (all-stages-valid, one-malformed-entry, header-only-empty), header and entry-zero templates.
- `constitution/` — full `constitution.template.md` with per-feature *and* project-wide aggregate concurrency/budget caps, structural-completeness validator, 2 fixtures.
- `skills/` — all 11 role skills (director, researcher, concept-writer, architecture-designer, architecture-critic, adr-maker, worker, code-reviewer, verifier, techwriter, pr-writer), each reviewed for trigger-accurate frontmatter and output-shape compatibility with the next role in the chain.
- `dashboard/` — FastAPI backend (`/log`, `/tasks`, `/panes`, `/config`, `/stats`; 12 passing tests, zero-outbound-calls enforced at the network layer) and a vanilla-JS 4-zone frontend (attention band, live panes, step-report feed, task board + totals panel), integration-tested against real fixture data.
- `docs/` — all 7 onboarding docs: getting-started, workflow-overview, human-gates, scaffolding-guide, constitution-authoring-guide, lifecycle-walkthrough, running-the-dashboard.
- `specs/README-template.md` — the director-maintained feature index.

**Known gaps, carried forward openly:**
- `scaffold/scaffold.sh` is not yet implemented — only its structural-completeness helper (`validate_constitution.py`) exists. Scaffolding a project from this tag currently requires following `docs/scaffolding-guide.md`'s steps by hand.
- The dashboard frontend has never been rendered in an actual browser (this environment had neither Node nor a browser available) — verified only via static-file-serving checks and a data-contract cross-read against the backend. See `dashboard/NOTES.md`.
- `/panes`' exact JSON response shape from `cmux list-panels`/`list-pane-surfaces` is implemented defensively but unconfirmed against a live cmux instance. See `dashboard/server/NOTES.md`.
- No established convention yet for a spawned pane to tag itself with its pipeline role, so `/panes`' `role` field is currently always `null`.
