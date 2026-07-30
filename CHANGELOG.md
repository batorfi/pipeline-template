# Changelog

Bundled versioning — one tag names one consistent state of skills, dashboard, log schema, and constitution template together. See `docs/scaffolding-guide.md` for what a version pin actually covers.

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
