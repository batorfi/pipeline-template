# pipeline-template

Canonical template repository for the Claude-only spec-driven multi-agent development pipeline. Every artifact a new project's scaffold needs — the 11 role skills, the dashboard (frontend + read-only Python backend), `factory-log.md`'s schema and templates, the constitution template, `scaffold.sh`, and onboarding docs — lives here, versioned as one bundle. See `docs/getting-started.md`.

Projects scaffold from a specific tagged version of this repository and never fork it — a fix belongs here, reviewed and re-tagged, not patched locally in a consuming project.

## Install and scaffold a new project

No local clone required — the template repo is public, so this works from a bare `curl`:

```bash
curl -fsSL https://raw.githubusercontent.com/batorfi/pipeline-template/main/install.sh \
  | bash -s -- --template-version v0.1.3 --target ./my-project
```

Or, if you already have the repo cloned:

```bash
scaffold/scaffold.sh --template-version v0.1.3 --target ./my-project
```

Both need only `git` (or `curl` + `tar` as a fallback with no `git` at all) — no GitHub auth of any kind, since the repo is public. See `docs/scaffolding-guide.md` for what happens next.

## Status: v0.1.3

- ✅ `factory-log/` — schema, validator, fixtures, templates (13 passing tests)
- ✅ `constitution/` — template, structural validator, fixtures
- ✅ `skills/` — all 11 role skills, reviewed
- ✅ `dashboard/` — backend (5 endpoints, FastAPI) and frontend (4-zone vanilla JS), integration-tested, confirmed rendering in cmux's actual embedded browser
- ✅ `docs/` — all 7 onboarding docs
- ✅ `scaffold/scaffold.sh` + `install.sh` — fresh scaffold + `--sync`, tested end-to-end against a real target and a real anonymous clone: clone (git or curl+tar, no auth needed against this public repo), copy, render, `<<FILL:...>>` validation gate, idempotency refusal, sync diff-preview, drifted-file overwrite with constitution-value preservation

See `docs/getting-started.md` for what this pipeline is, and the source project's `docs/implementation-plan.md` / `implementation-specs.md` / `implementation-tasks.md` for the full build plan this repository is being assembled against.
