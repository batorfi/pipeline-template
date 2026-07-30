# pipeline-template

Canonical template repository for the Claude-only spec-driven multi-agent development pipeline. Every artifact a new project's scaffold needs — the 11 role skills, the dashboard (frontend + read-only Python backend), `factory-log.md`'s schema and templates, the constitution template, and onboarding docs — lives here, versioned as one bundle. See `docs/getting-started.md`.

Projects scaffold from a specific tagged version of this repository (`scaffold/scaffold.sh --template-version <tag> --target ./my-project`) and never fork it — a fix belongs here, reviewed and re-tagged, not patched locally in a consuming project.

## Status: v0.1.0 in progress

- ✅ `factory-log/` — schema, validator, fixtures, templates (12 passing tests)
- ✅ `constitution/` — template, structural validator, fixtures
- ✅ `skills/` — all 11 role skills, reviewed
- ✅ `dashboard/` — backend (5 endpoints, FastAPI) and frontend (4-zone vanilla JS), integration-tested
- ✅ `docs/` — all 7 onboarding docs
- ⏳ `scaffold/scaffold.sh` — not yet implemented (Phase 4)
- ⏳ Live-`cmux` verification of the dashboard frontend and the `/panes` response shape — not yet done (needs a live cmux session)

See `docs/getting-started.md` for what this pipeline is, and the source project's `docs/implementation-plan.md` / `implementation-specs.md` / `implementation-tasks.md` for the full build plan this repository is being assembled against.
