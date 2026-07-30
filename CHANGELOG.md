# Changelog

Bundled versioning — one tag names one consistent state of skills, dashboard, log schema, and constitution template together. See `docs/scaffolding-guide.md` for what a version pin actually covers.

## v0.1.4 — 2026-07-30

**Fixed:**
- Both `install.sh` and `scaffold/scaffold.sh` now check for `uv` up front and fail with a clear, actionable install link if it's missing, instead of failing deep inside a `uv run` invocation with a generic "command not found." `uv` is a stated hard dependency (not silently worked around), so this is a fast, honest failure rather than a fallback.
- Local working-copy drift fixed: `README.md` and `CHANGELOG.md` in the source project's `outcomes/pipeline-template/` had gone stale (only ever updated in throwaway publish clones, never synced back) — resolved by pulling the published state back into the working copy before this release, so the two stay in sync going forward.

**Changed:**
- `README.md` restructured as an actual onboarding entry point — prerequisites, a 3-step getting-started flow, and a table routing to the right doc for what you're trying to do — rather than a status page with a getting-started link buried in prose.

## v0.1.3 — 2026-07-30

Repository visibility changed to **public**. This release makes the tooling reflect that.

**Added:**
- `install.sh` — a bootstrap installer at the repo root enabling `curl -fsSL .../install.sh | bash -s -- --template-version <tag> --target ./my-project` with no local clone required. Uses `git clone` if available, falls back to downloading the tagged tarball via `curl` + `tar` if `git` isn't present, and delegates all real scaffolding logic to `scaffold/scaffold.sh` inside the fetched copy — no logic duplicated between the two.

**Changed:**
- `scaffold/scaffold.py`'s clone step no longer requires `gh` or any authentication. Since the repo is public, a plain `git clone` works unauthenticated; `gh repo clone` is still tried first if `gh` is installed (marginally more resilient behind some proxies), but any `gh` failure — including "not authenticated" — now falls through to plain `git` instead of aborting. Confirmed by removing `gh` from `PATH` entirely and re-running a fresh scaffold successfully.
- `docs/scaffolding-guide.md` and the README now document the `curl | bash` install path as the primary way to scaffold a new project.

**Fixed nothing new** in this release beyond the above — see v0.1.2 for the dashboard project-root fix and v0.1.1 for `scaffold.sh` itself.

## v0.1.2 — 2026-07-30

**Fixed:**
- **`dashboard/server/app_config.py`: project-root resolution silently broke on the normal invocation.** `DashboardConfig.load()` computed `project_root` as `config_json_path.parent.parent`, which only worked when the config path was already absolute. The real, documented invocation (`PIPELINE_CONFIG=config.json`, a bare filename) hit a pathlib quirk — `Path(".").parent` is also `Path(".")`, since `.parent` is lexical, not filesystem-aware — so `project_root` silently collapsed to the server's `cwd` instead of the real project root. Every downstream path (`factory_log_path`, `constitution_path`) then pointed at files that don't exist, which `/log`/`/tasks` treat as valid empty state by design — so the failure was silent: no exception, no error, just an API that always looked like a freshly-scaffolded empty project no matter what was actually in the log. Found only by running a real server and hitting it with real `curl` requests — every existing test used an already-absolute config path and never exercised this. Fixed by resolving the config path to absolute before computing `.parent.parent`; added a regression test that changes the test process's `cwd` and passes a bare filename.
- **`docs/running-the-dashboard.md`: the documented two-process approach (separate backend and static-file-server processes) never actually worked.** The frontend's `fetch()` calls are relative, same-origin paths — they have no way to reach an API on a different port. Rewritten to the single-process form (FastAPI serving both the API and the static frontend via a `StaticFiles` mount), which is what was actually verified working end-to-end.

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
