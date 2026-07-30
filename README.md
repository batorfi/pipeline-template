# AI Software Factory Pipeline Template

*(repository: [`pipeline-template`](https://github.com/batorfi/pipeline-template) — the repo slug and all clone/install URLs stay unchanged; this is a display-name update only.)*

**New here?** Read [`docs/introduction.md`](docs/introduction.md) first — the motivation, design reasoning, architectural perspective, and implementation principles behind this pipeline, for anyone evaluating whether it fits their situation before diving into how to run it.

Canonical template repository for the Claude-only spec-driven multi-agent development pipeline: one persistent **director** pane coordinates a feature's entire lifecycle — from a raw idea to an opened merge request — spawning ephemeral Claude Code panes for each stage, running GitHub Spec Kit's phases, and stopping at nine human gates along the way.

Every artifact a new project's scaffold needs — the 11 role skills, the dashboard (frontend + read-only Python backend), `factory-log.md`'s schema and templates, the constitution template, `scaffold.sh`, and onboarding docs — lives here, versioned as one bundle. Projects scaffold from a specific tagged version of this repository and never fork it — a fix belongs here, reviewed and re-tagged, not patched locally in a consuming project.

## What this is, who it's for, and why

**What it is.** A reusable template for bootstrapping a *spec-driven, gated, cost-tiered* Claude Code pipeline into any codebase — not a framework you import, a set of files (skills, a constitution, a dashboard, scaffolding tooling) you pull into a project once and then run features through, versioned and re-synced like any other dependency.

**Who it's for.** Anyone running non-trivial feature work through Claude Code who wants more structure than an ad hoc prompt-per-task loop, but doesn't want to build the scaffolding themselves — solo engineers and small teams in particular, since the whole design assumes one human approving gates, not a review board. It was built for, and is actively used by, the maintainer's own projects first; it's public so anyone in the same situation can use it too, and so fixes and improvements have somewhere real to land instead of drifting apart across private forks.

**Why it exists.** Handing an agent a task with no shared, explicit specification has a predictable failure mode: "done" becomes whatever the agent decided it meant, scope creeps past the boundary you intended, and there's no reliable signal for which tasks are safe to run in parallel without conflicting — this holds even with a very capable model, just less severely. This pipeline exists to fix that without inventing a bespoke process: it puts GitHub Spec Kit's spec → plan → tasks artifacts at the center (so `[P]`-tagged, file-scoped task lines double as the parallel-dispatch contract for free), wraps them in nine explicit human gates so nothing ships without a decision you actually made, and tiers cost (Opus/Sonnet/Haiku) by the actual consequence of a role's mistake rather than treating every step as equally expensive or equally trustworthy.

## Prerequisites

- **[`uv`](https://docs.astral.sh/uv/getting-started/installation/)** — required. Both [`install.sh`](install.sh) and [`scaffold/scaffold.sh`](scaffold/scaffold.sh) check for it up front and fail with an install link if it's missing, rather than a confusing error partway through.
- **`git`** — recommended. If it's not present, the installer falls back to a `curl` + `tar` tarball download instead.
- **[`cmux`](https://cmux.com)** — needed to actually *run* a scaffolded project (it's what the director and worker panes run inside), not to scaffold one.
- **[GitHub Spec Kit](https://github.com/github/spec-kit)** (`specify` CLI) — install command and order in step 1 of Getting Started, below. `scaffold.sh` will warn and skip `specify init` if it's not installed yet, so you can scaffold first and install it before your first feature if you'd rather.

No GitHub account or auth of any kind is needed — this repository is public.

## Getting started

**1. Install GitHub Spec Kit's `specify` CLI** — the scaffold step below will use it automatically if it's already on `PATH`, so install it first if you can:

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify --version   # confirm it installed correctly
```

*(The `uv tool install` line itself is still unverified by this repository — see the Status section. `specify init . --integration claude` is confirmed working in real use once `specify` is on `PATH`, including installing all of Spec Kit's own skills correctly. If the install command above doesn't work for you, check [GitHub Spec Kit's own install docs](https://github.com/github/spec-kit) directly.)*

If you skip this step, `scaffold.sh` will warn and continue without it — you can install it later and run `specify init . --integration claude` by hand inside the project folder once it's scaffolded (step 2 creates that folder for you; no separate `mkdir` is needed).

**2. Scaffold — either a brand-new project, or into a codebase you already have:**

*New project* — creates `./my-project` itself, target doesn't need to exist beforehand:

```bash
curl -fsSL https://raw.githubusercontent.com/batorfi/pipeline-template/main/install.sh \
  | bash -s -- --template-version v0.1.19 --target ./my-project
```

*Existing project* — point `--target` at your existing repository's root instead:

```bash
curl -fsSL https://raw.githubusercontent.com/batorfi/pipeline-template/main/install.sh \
  | bash -s -- --template-version v0.1.19 --target ./my-existing-repo
```

Your existing files, git history, and `.git/` are left untouched — the scaffold only adds `.claude/skills-pipeline-roles/`, `.specify/`, `dashboard/`, `docs/`, and `specs/`. **If your project already has non-empty `dashboard/` or `docs/` directories, the scaffold refuses to run** rather than silently deleting and replacing them (this pipeline's own artifacts use those same directory names) — move your existing one aside first, or scaffold into a subdirectory instead of the project root.

If `specify` from step 1 is on `PATH`, either form runs `specify init . --integration claude` inside the target automatically. (Or, from an existing local clone of this repo: `scaffold/scaffold.sh --template-version v0.1.19 --target <path>`.)

**3. Follow the printed checklist** — fill in `constitution.md`'s `<<FILL:...>>` markers, stand up the 3 cmux workspaces, start the dashboard in a side pane of main, and run one deliberately trivial synthetic feature through all 9 gates by hand before trusting it with anything real.

The cmux-workspace step has three equivalent paths — pick whichever fits how you work: [`scaffold/prompts/setup-cmux-workspaces.md`](scaffold/prompts/setup-cmux-workspaces.md) (paste its prompt into a Claude Code session running inside cmux — copied into your scaffolded project as `docs/prompts/setup-cmux-workspaces.md`; see "How to run a `docs/prompts/*.md` file" in [`docs/scaffolding-guide.md`](docs/scaffolding-guide.md)), [`docs/manual-cmux-workspace-setup.md`](docs/manual-cmux-workspace-setup.md) (run the `cmux` CLI commands yourself), or [`docs/manual-cmux-workspace-setup-gui.md`](docs/manual-cmux-workspace-setup-gui.md) (create and name the workspaces in the cmux app's UI, with one CLI lookup at the very end to read off their IDs). The dashboard step similarly uses [`scaffold/prompts/run-dashboard-in-pane.md`](scaffold/prompts/run-dashboard-in-pane.md) (copied to `docs/prompts/run-dashboard-in-pane.md`) or the manual commands in [`docs/running-the-dashboard.md`](docs/running-the-dashboard.md). All five files are copied into your project at scaffold time.

**4. Read the rest of `docs/` as you need it** — this is the map:

| If you want to... | Read |
|---|---|
| Understand the motivation, architecture, and design reasoning in depth | [`docs/introduction.md`](docs/introduction.md) |
| Understand what this pipeline is, in brief | [`docs/getting-started.md`](docs/getting-started.md) |
| See the full role/gate/tier design before running it | [`docs/workflow-overview.md`](docs/workflow-overview.md) |
| Know what an open gate is actually asking of you | [`docs/human-gates.md`](docs/human-gates.md) |
| Scaffold or sync a project | [`docs/scaffolding-guide.md`](docs/scaffolding-guide.md) |
| Stand up the 3 cmux workspaces with a real name→ID mapping | [`scaffold/prompts/setup-cmux-workspaces.md`](scaffold/prompts/setup-cmux-workspaces.md) (paste into a Claude Code session in cmux), [`docs/manual-cmux-workspace-setup.md`](docs/manual-cmux-workspace-setup.md) (run the `cmux` commands yourself), or [`docs/manual-cmux-workspace-setup-gui.md`](docs/manual-cmux-workspace-setup-gui.md) (create/name them in the cmux app's UI, one CLI lookup at the end) |
| Fill in `constitution.md` with real values | [`docs/constitution-authoring-guide.md`](docs/constitution-authoring-guide.md) |
| See the whole empty-repo-to-ongoing-delivery story in one read | [`docs/lifecycle-walkthrough.md`](docs/lifecycle-walkthrough.md) |
| Get the dashboard running (in a cmux pane or standalone) and troubleshoot it | [`docs/running-the-dashboard.md`](docs/running-the-dashboard.md), [`scaffold/prompts/run-dashboard-in-pane.md`](scaffold/prompts/run-dashboard-in-pane.md) (copied to `docs/prompts/` in your scaffolded project) |

## Status: v0.1.19

- ✅ `factory-log/` — schema, validator, fixtures, templates (13 passing tests)
- ✅ `constitution/` — template, structural validator, fixtures
- ✅ `skills/` — all 11 role skills, reviewed; director skill now reads `.specify/cmux-workspaces.json` for real workspace IDs instead of assuming cmux understands workspace names
- ✅ `dashboard/` — backend (5 endpoints, FastAPI) and frontend (4-zone vanilla JS), integration-tested, confirmed rendering in cmux's actual embedded browser. **Two real scaffolded-project bugs found and fixed**, both only surfacing once someone actually ran the scaffold and started the dashboard for real: (1) the backend imports `factory-log/validator.py` from a fixed project-root-relative path, but scaffolding never copied `factory-log/` into the project at all — fixed by copying `factory-log/validator.py` and `factory-log/SCHEMA.md` in both `do_copy_steps` and `--sync`; (2) `dashboard/config.json` was documented as "generated by `scaffold.sh`" but nothing ever generated it — fixed by a new `write_dashboard_config()` step, plus a related bug caught before shipping where `--sync`'s wholesale `dashboard/` overwrite would have silently deleted an existing `config.json` (now preserved across sync). Confirmed against a real scaffolded project: backend starts, `/log` and `/` both respond correctly.
- ✅ [`docs/`](docs/) — all 10 onboarding docs, including [`introduction.md`](docs/introduction.md) (motivation, architecture, implementation principles), [`manual-cmux-workspace-setup.md`](docs/manual-cmux-workspace-setup.md) (run the cmux commands yourself), and [`manual-cmux-workspace-setup-gui.md`](docs/manual-cmux-workspace-setup-gui.md) (create workspaces in the cmux app's UI, one CLI lookup at the end) — three alternative paths for the same cmux-workspace setup step
- ✅ [`scaffold/scaffold.sh`](scaffold/scaffold.sh) + [`install.sh`](install.sh) — fresh scaffold + `--sync`, tested end-to-end against a real target and a real anonymous clone: clone (git or curl+tar, no auth needed against this public repo), copy, render, `<<FILL:...>>` validation gate, idempotency refusal, sync diff-preview, drifted-file overwrite with constitution-value preservation, a fail-fast check for `uv` before either script does anything else, and — for scaffolding into an existing project — a pre-flight check that refuses to run rather than silently deleting a pre-existing non-empty `dashboard/` or `docs/`, tested against both a real conflict and a real non-conflicting existing project
- ⚠️ [`scaffold/prompts/setup-cmux-workspaces.md`](scaffold/prompts/setup-cmux-workspaces.md) and [`run-dashboard-in-pane.md`](scaffold/prompts/run-dashboard-in-pane.md) — now copied into every scaffolded project as `docs/prompts/` so a developer can actually find them after `scaffold.sh` exits (previously they only existed in this template repo, unreachable from a scaffolded project). Content itself is unchanged: written from the cmux CLI reference doc, **not yet run against a live cmux instance**; the dashboard-starting commands inside the second prompt are fully verified, the cmux pane-mechanics wrapping them is not. Each prompt states this caveat and asks you to report back what actually happens.
- ✅ `specify init . --integration claude`, run manually — **confirmed working against a real Spec Kit install**, twice: all 10 of Spec Kit's own skills installed correctly alongside our 11 role skills with zero naming collisions (validating the `.claude/skills-pipeline-roles/` naming choice made specifically to avoid this), and — on a second, correct run — Spec Kit's own "existing file preserved" logic confirmed it doesn't overwrite an already-filled-in `constitution.md`. The `uv tool install specify-cli` line in Getting Started step 1 is still unverified by us specifically (the confirming user already had `specify` installed by another method).
- ✅ `specify init` run **automatically** by `scaffold.sh` — **fixed and confirmed**: it used to always fail in practice, because by the time it runs the target is already non-empty (our own scaffold populated it first), triggering an interactive "continue? [y/N]" prompt with nothing to read from, since the automated path (e.g. `curl | bash`) has no TTY attached. `scaffold.py` now feeds `y` to that prompt automatically, and a real `curl | bash` run confirmed it: all 10 Spec Kit skills installed, `.specify/` fully populated, rendered constitution preserved, no further prompts encountered.
- ✅ Real-world lesson from that same pilot, now fixed and re-confirmed: an earlier run of `specify init` from the wrong directory (a project's parent, not the project itself) installed Spec Kit there instead of inside the target — fully recoverable (nothing pre-existing was overwritten), but avoidable. `scaffold.sh`'s printed checklist now embeds the literal target path and warns about this explicitly; the very next scaffold run, following the corrected checklist, went cleanly.
- ✅ `install.sh`'s git output — **fixed and verified**: cloning an annotated release tag used to print `git`'s own noise (`Cloning into...`, `warning: refs/tags/... is not a commit!`, a detached-HEAD advice block) straight to the terminal on every run. Now captured silently and only shown in full if the clone actually fails, verified against both a clean success (no output at all) and a real failure (bad tag — full diagnostic output shown).

See the source project's `docs/implementation-plan.md` / `implementation-specs.md` / `implementation-tasks.md` for the full build plan this repository is being assembled against — not part of this repo, but the design record behind it.
