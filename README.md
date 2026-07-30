# AI Software Factory Pipeline Template

*(repository: [`pipeline-template`](https://github.com/batorfi/pipeline-template) — the repo slug and all clone/install URLs stay unchanged; this is a display-name update only.)*

Canonical template repository for the Claude-only spec-driven multi-agent development pipeline: one persistent **director** pane coordinates a feature's entire lifecycle — from a raw idea to an opened merge request — spawning ephemeral Claude Code panes for each stage, running GitHub Spec Kit's phases, and stopping at nine human gates along the way.

Every artifact a new project's scaffold needs — the 11 role skills, the dashboard (frontend + read-only Python backend), `factory-log.md`'s schema and templates, the constitution template, `scaffold.sh`, and onboarding docs — lives here, versioned as one bundle. Projects scaffold from a specific tagged version of this repository and never fork it — a fix belongs here, reviewed and re-tagged, not patched locally in a consuming project.

## What this is, who it's for, and why

**What it is.** A reusable template for bootstrapping a *spec-driven, gated, cost-tiered* Claude Code pipeline into any codebase — not a framework you import, a set of files (skills, a constitution, a dashboard, scaffolding tooling) you pull into a project once and then run features through, versioned and re-synced like any other dependency.

**Who it's for.** Anyone running non-trivial feature work through Claude Code who wants more structure than an ad hoc prompt-per-task loop, but doesn't want to build the scaffolding themselves — solo engineers and small teams in particular, since the whole design assumes one human approving gates, not a review board. It was built for, and is actively used by, the maintainer's own projects first; it's public so anyone in the same situation can use it too, and so fixes and improvements have somewhere real to land instead of drifting apart across private forks.

**Why it exists.** Handing an agent a task with no shared, explicit specification has a predictable failure mode: "done" becomes whatever the agent decided it meant, scope creeps past the boundary you intended, and there's no reliable signal for which tasks are safe to run in parallel without conflicting — this holds even with a very capable model, just less severely. This pipeline exists to fix that without inventing a bespoke process: it puts GitHub Spec Kit's spec → plan → tasks artifacts at the center (so `[P]`-tagged, file-scoped task lines double as the parallel-dispatch contract for free), wraps them in nine explicit human gates so nothing ships without a decision you actually made, and tiers cost (Opus/Sonnet/Haiku) by the actual consequence of a role's mistake rather than treating every step as equally expensive or equally trustworthy.

## Prerequisites

- **[`uv`](https://docs.astral.sh/uv/getting-started/installation/)** — required. Both `install.sh` and `scaffold/scaffold.sh` check for it up front and fail with an install link if it's missing, rather than a confusing error partway through.
- **`git`** — recommended. If it's not present, the installer falls back to a `curl` + `tar` tarball download instead.
- **[`cmux`](https://cmux.com)** and **[GitHub Spec Kit](https://github.com/github/spec-kit)** (`specify` CLI) — needed to actually *run* a scaffolded project, not to scaffold one. `scaffold.sh` will warn and skip `specify init` if it's not installed yet, so you can scaffold first and install these before your first feature.

No GitHub account or auth of any kind is needed — this repository is public.

## Getting started

**1. Scaffold a new project** — no local clone required:

```bash
curl -fsSL https://raw.githubusercontent.com/batorfi/pipeline-template/main/install.sh \
  | bash -s -- --template-version v0.1.7 --target ./my-project
```

(Or, from an existing local clone: `scaffold/scaffold.sh --template-version v0.1.7 --target ./my-project`.)

**2. Follow the printed checklist** — fill in `constitution.md`'s `<<FILL:...>>` markers, stand up the 3 cmux workspaces (`scaffold/prompts/setup-cmux-workspaces.md`), start the dashboard in a side pane of main (`scaffold/prompts/run-dashboard-in-pane.md`), and run one deliberately trivial synthetic feature through all 9 gates by hand before trusting it with anything real. Full walkthrough: `docs/scaffolding-guide.md`.

**3. Read the rest of `docs/` as you need it** — this is the map:

| If you want to... | Read |
|---|---|
| Understand what this pipeline is, in brief | `docs/getting-started.md` |
| See the full role/gate/tier design before running it | `docs/workflow-overview.md` |
| Know what an open gate is actually asking of you | `docs/human-gates.md` |
| Scaffold or sync a project | `docs/scaffolding-guide.md` |
| Stand up the 3 cmux workspaces with a real name→ID mapping | `scaffold/prompts/setup-cmux-workspaces.md` |
| Fill in `constitution.md` with real values | `docs/constitution-authoring-guide.md` |
| See the whole empty-repo-to-ongoing-delivery story in one read | `docs/lifecycle-walkthrough.md` |
| Get the dashboard running (in a cmux pane or standalone) and troubleshoot it | `docs/running-the-dashboard.md`, `scaffold/prompts/run-dashboard-in-pane.md` |

## Status: v0.1.7

- ✅ `factory-log/` — schema, validator, fixtures, templates (13 passing tests)
- ✅ `constitution/` — template, structural validator, fixtures
- ✅ `skills/` — all 11 role skills, reviewed; director skill now reads `.specify/cmux-workspaces.json` for real workspace IDs instead of assuming cmux understands workspace names
- ✅ `dashboard/` — backend (5 endpoints, FastAPI) and frontend (4-zone vanilla JS), integration-tested, confirmed rendering in cmux's actual embedded browser
- ✅ `docs/` — all 7 onboarding docs
- ✅ `scaffold/scaffold.sh` + `install.sh` — fresh scaffold + `--sync`, tested end-to-end against a real target and a real anonymous clone: clone (git or curl+tar, no auth needed against this public repo), copy, render, `<<FILL:...>>` validation gate, idempotency refusal, sync diff-preview, drifted-file overwrite with constitution-value preservation, and a fail-fast check for `uv` before either script does anything else
- ⚠️ `scaffold/prompts/setup-cmux-workspaces.md` and `run-dashboard-in-pane.md` — written from the cmux CLI reference doc, **not yet run against a live cmux instance**; the dashboard-starting commands inside the second prompt are fully verified, the cmux pane-mechanics wrapping them is not. Each prompt states this caveat and asks you to report back what actually happens.

See the source project's `docs/implementation-plan.md` / `implementation-specs.md` / `implementation-tasks.md` for the full build plan this repository is being assembled against — not part of this repo, but the design record behind it.
