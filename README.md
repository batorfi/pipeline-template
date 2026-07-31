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
  | bash -s -- --template-version v0.1.34 --target ./my-project
```

*Existing project* — point `--target` at your existing repository's root instead:

```bash
curl -fsSL https://raw.githubusercontent.com/batorfi/pipeline-template/main/install.sh \
  | bash -s -- --template-version v0.1.34 --target ./my-existing-repo
```

Your existing files, git history, and `.git/` are left untouched — the scaffold only adds `.claude/skills-pipeline-roles/`, `.specify/`, `dashboard/`, `docs/`, and `specs/`. **If your project already has non-empty `dashboard/` or `docs/` directories, the scaffold refuses to run** rather than silently deleting and replacing them (this pipeline's own artifacts use those same directory names) — move your existing one aside first, or scaffold into a subdirectory instead of the project root.

If `specify` from step 1 is on `PATH`, either form runs `specify init . --integration claude` inside the target automatically. (Or, from an existing local clone of this repo: `scaffold/scaffold.sh --template-version v0.1.34 --target <path>`.)

**3. Follow the printed checklist** — fill in `constitution.md`'s `<<FILL:...>>` markers, stand up the 3 cmux workspaces, start the dashboard in a side pane of main, and run one deliberately trivial synthetic feature through all 9 gates by hand before trusting it with anything real. For that last step — actually starting the director and responding at a gate — see [`docs/working-with-the-director.md`](docs/working-with-the-director.md).

The cmux-workspace step: run `docs/setup-cmux-workspaces.sh` from your project root, in the workspace you want as main — it names each workspace `<project>-main`/`-design`/`-implementation` so the cmux sidebar reads clearly at a glance, and writes `.specify/cmux-workspaces.json`. See [`docs/manual-cmux-workspace-setup.md`](docs/manual-cmux-workspace-setup.md) for what it does or to run the same commands by hand. The dashboard step uses [`scaffold/prompts/run-dashboard-in-pane.md`](scaffold/prompts/run-dashboard-in-pane.md) (paste its prompt into a Claude Code session running inside cmux — copied into your scaffolded project as `docs/prompts/run-dashboard-in-pane.md`; see "How to run a `docs/prompts/*.md` file" in [`docs/scaffolding-guide.md`](docs/scaffolding-guide.md)) or the manual commands in [`docs/running-the-dashboard.md`](docs/running-the-dashboard.md).

**4. Read the rest of `docs/` as you need it** — this is the map:

| If you want to... | Read |
|---|---|
| Understand the motivation, architecture, and design reasoning in depth | [`docs/introduction.md`](docs/introduction.md) |
| Understand what this pipeline is, in brief | [`docs/getting-started.md`](docs/getting-started.md) |
| See the full role/gate/tier design before running it | [`docs/workflow-overview.md`](docs/workflow-overview.md) |
| Know what an open gate is actually asking of you | [`docs/human-gates.md`](docs/human-gates.md) |
| Scaffold or sync a project | [`docs/scaffolding-guide.md`](docs/scaffolding-guide.md) |
| Stand up the 3 cmux workspaces with a real name→ID mapping | `docs/setup-cmux-workspaces.sh` (run it); [`docs/manual-cmux-workspace-setup.md`](docs/manual-cmux-workspace-setup.md) (what it does, or do it by hand) |
| Fill in `constitution.md` with real values | [`docs/constitution-authoring-guide.md`](docs/constitution-authoring-guide.md) |
| Actually start the director and respond at a gate | [`docs/working-with-the-director.md`](docs/working-with-the-director.md) |
| See the whole empty-repo-to-ongoing-delivery story in one read | [`docs/lifecycle-walkthrough.md`](docs/lifecycle-walkthrough.md) |
| Get the dashboard running (in a cmux pane or standalone) and troubleshoot it | [`docs/running-the-dashboard.md`](docs/running-the-dashboard.md), [`scaffold/prompts/run-dashboard-in-pane.md`](scaffold/prompts/run-dashboard-in-pane.md) (copied to `docs/prompts/` in your scaffolded project) |

## Status: v0.1.34

- ✅ `factory-log/` — schema, validator, fixtures, templates (26 passing tests)
- ✅ `constitution/` — template, structural validator, fixtures
- ✅ `skills/` — all 11 role skills, reviewed; director skill now reads `.specify/cmux-workspaces.json` for real workspace IDs instead of assuming cmux understands workspace names. **Critical bug found and fixed**: these were only ever copied into `.claude/skills-pipeline-roles/`, a non-standard directory Claude Code's own skill discovery doesn't scan — so no role skill, including director, was ever actually loadable in any scaffolded project, discovered when a real user asked Claude Code for its skillset and saw only Spec Kit's `speckit-*` skills. Now also copied into `.claude/skills/` directly (no naming collisions with `speckit-*`), confirmed against a simulated pre-existing Spec Kit install and applied by hand to fix a real already-scaffolded project. **Second real process gap found and fixed**: nothing ever told the director to check off `tasks.md` as work completed — a real dry run confirmed via `factory-log.md` that most tasks had genuinely finished, yet only 3 of 36 checkboxes were ever flipped, making the dashboard's Task Board look almost entirely undone on a feature that had already reached the PR gate. The director skill's fan-out/implementation step now explicitly owns marking `tasks.md`'s checkboxes.
- ✅ `dashboard/` — backend (5 endpoints, FastAPI) and frontend (4-zone vanilla JS), integration-tested, confirmed rendering in cmux's actual embedded browser. **Four real scaffolded-project bugs found and fixed**, each only surfacing once someone actually ran the scaffold, started the dashboard, and ran a real feature through it: (1) the backend imports `factory-log/validator.py` from a fixed project-root-relative path, but scaffolding never copied `factory-log/` into the project at all — fixed by copying `factory-log/validator.py` and `factory-log/SCHEMA.md` in both `do_copy_steps` and `--sync`; (2) `dashboard/config.json` was documented as "generated by `scaffold.sh`" but nothing ever generated it — fixed by a new `write_dashboard_config()` step, plus a related bug caught before shipping where `--sync`'s wholesale `dashboard/` overwrite would have silently deleted an existing `config.json` (now preserved across sync); (3) the Task Board stayed permanently empty against a real, active feature — `config.json`'s `tasks_path` is a static value that can never match Spec Kit's actual per-feature `specs/<NNN-slug>/tasks.md` convention, fixed by `DashboardConfig.resolve_tasks_path()` falling back to the most recently modified `specs/*/tasks.md` when the configured path doesn't exist; (4) "Running Now" (live panes) always reported empty even with real panes running — three compounding bugs (wrong JSON key expected from `cmux list-panels`, no `--workspace` scoping so the backend could only ever see its own workspace, and a frontend status filter no real cmux data could ever satisfy), all fixed and confirmed against 9 real panes across main/design/implementation mid-dry-run. Confirmed against a real scaffolded project and a real dry-run feature: backend starts, `/log`, `/`, `/tasks`, and `/panes` all respond correctly with real data. **Real token usage added**, replacing the previously-universal `$0.00`: `cmux` exposes no cost/token data of its own, but a Claude-session pane's local transcript (`~/.claude/projects/<slug>/<checkpoint-id>.jsonl`, keyed by `resume_binding.checkpoint_id`) does — `token_usage_reader.py` sums real per-turn `usage` blocks from it, confirmed against a real transcript showing hundreds of thousands of real tokens per pane. The TOTALS panel (renamed "Live Token Usage") now aggregates this across all currently-open panes instead of showing `$0.00` from `/stats`'s still-placeholder historical figures — a real ~607k-token total across 6 active panes confirmed live. Explicitly a live snapshot of open panes only, not a full-feature historical total; closed panes' usage isn't retained anywhere once their pane closes.
- ✅ [`docs/`](docs/) — all 10 onboarding docs, including [`introduction.md`](docs/introduction.md) (motivation, architecture, implementation principles), and [`working-with-the-director.md`](docs/working-with-the-director.md) (the mechanics of starting the director and responding at a gate, including a clarification that the dashboard has no functional approve button and never will — it's read-only by design)
- ✅ `docs/setup-cmux-workspaces.sh` + [`docs/manual-cmux-workspace-setup.md`](docs/manual-cmux-workspace-setup.md) — **confirmed against a real cmux instance**, across several real runs that each caught and fixed a real bug: an earlier draft's copy-pasteable example used a literal `<design-id>` placeholder in an unquoted bash command, which the shell parsed as input redirection instead of a value to substitute; `cmux workspace rename` turned out to require **both** `--workspace <id>` and `--title <name>` explicitly, with no "rename the current workspace" shorthand (two separate real failures caught this — a missing `--title` and a missing `--workspace`). Also confirmed: both `cmux workspace create` and `cmux workspace rename` print the affected workspace's ID directly in their own output (`OK workspace:<n>`), so no before/after `workspace list` diff is needed; the JSON key for a workspace's ID is `ref` (`workspace_ref` one level up in `current-workspace --json`). The whole sequence is now packaged as `docs/setup-cmux-workspaces.sh`, copied into every scaffolded project (`do_copy_steps` and `--sync`) so there's one correct, executable script instead of copy-pasteable commands prone to exactly this class of error — `docs/manual-cmux-workspace-setup.md` now documents both the script and the equivalent by-hand steps.
- ✅ [`scaffold/scaffold.sh`](scaffold/scaffold.sh) + [`install.sh`](install.sh) — fresh scaffold + `--sync`, tested end-to-end against a real target and a real anonymous clone: clone (git or curl+tar, no auth needed against this public repo), copy, render, `<<FILL:...>>` validation gate, idempotency refusal, sync diff-preview, drifted-file overwrite with constitution-value preservation, a fail-fast check for `uv` before either script does anything else, and — for scaffolding into an existing project — a pre-flight check that refuses to run rather than silently deleting a pre-existing non-empty `dashboard/` or `docs/`, tested against both a real conflict and a real non-conflicting existing project
- ⚠️ [`scaffold/prompts/run-dashboard-in-pane.md`](scaffold/prompts/run-dashboard-in-pane.md) — copied into every scaffolded project as `docs/prompts/run-dashboard-in-pane.md` so a developer can actually find it after `scaffold.sh` exits. Written from the cmux CLI reference doc, **not yet run against a live cmux instance**; the dashboard-starting command itself is fully verified, the cmux pane-mechanics wrapping it (`cmux new-split`) is not. States this caveat and asks you to report back what actually happens. (The earlier prompt-based and GUI-based cmux-workspace-setup docs were removed in favor of a single CLI-based path — see `docs/manual-cmux-workspace-setup.md`.)
- ✅ `specify init . --integration claude`, run manually — **confirmed working against a real Spec Kit install**, twice: all 10 of Spec Kit's own skills installed correctly alongside our 11 role skills with zero naming collisions (validating the `.claude/skills-pipeline-roles/` naming choice made specifically to avoid this), and — on a second, correct run — Spec Kit's own "existing file preserved" logic confirmed it doesn't overwrite an already-filled-in `constitution.md`. The `uv tool install specify-cli` line in Getting Started step 1 is still unverified by us specifically (the confirming user already had `specify` installed by another method).
- ✅ `specify init` run **automatically** by `scaffold.sh` — **fixed and confirmed**: it used to always fail in practice, because by the time it runs the target is already non-empty (our own scaffold populated it first), triggering an interactive "continue? [y/N]" prompt with nothing to read from, since the automated path (e.g. `curl | bash`) has no TTY attached. `scaffold.py` now feeds `y` to that prompt automatically, and a real `curl | bash` run confirmed it: all 10 Spec Kit skills installed, `.specify/` fully populated, rendered constitution preserved, no further prompts encountered.
- ✅ Real-world lesson from that same pilot, now fixed and re-confirmed: an earlier run of `specify init` from the wrong directory (a project's parent, not the project itself) installed Spec Kit there instead of inside the target — fully recoverable (nothing pre-existing was overwritten), but avoidable. `scaffold.sh`'s printed checklist now embeds the literal target path and warns about this explicitly; the very next scaffold run, following the corrected checklist, went cleanly.
- ✅ `install.sh`'s git output — **fixed and verified**: cloning an annotated release tag used to print `git`'s own noise (`Cloning into...`, `warning: refs/tags/... is not a commit!`, a detached-HEAD advice block) straight to the terminal on every run. Now captured silently and only shown in full if the clone actually fails, verified against both a clean success (no output at all) and a real failure (bad tag — full diagnostic output shown).

See the source project's `docs/implementation-plan.md` / `implementation-specs.md` / `implementation-tasks.md` for the full build plan this repository is being assembled against — not part of this repo, but the design record behind it.
