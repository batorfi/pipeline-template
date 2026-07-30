# Scaffolding guide

Condensed from `concepts/claude-only-pipeline/20260720-113747_repeatable-codebase-scaffold-for-the-claude-only-pipeline.md` — read that concept for full rationale.

## Running scaffold.sh

Directly from the web, no local clone needed (the repo is public, so this needs no GitHub auth):

```bash
curl -fsSL https://raw.githubusercontent.com/batorfi/pipeline-template/main/install.sh \
  | bash -s -- --template-version <pinned-tag> --target ./my-project
```

Or, from an existing local clone:

```bash
scaffold/scaffold.sh --template-version <pinned-tag> --target ./my-project
```

This mechanizes steps 1, 2, 3, 5, 6, and the file-copy portion of 7 in one command: clones this template repo at the pinned tag (plain `git clone`, or `gh repo clone` if `gh` happens to be installed — neither requires auth against a public repo), git-inits the target if needed, copies skills/dashboard/docs/specs-README, renders `constitution.template.md` and the factory-log templates, and runs `specify init`. Steps 4 (cmux workspaces) and the remainder of 7 (actually starting and confirming the dashboard) are not run by `scaffold.sh` itself — they need cmux running, which a scaffold script can't assume — use the prompts named in each step below instead. Step 8 is never automated, on purpose.

## How to run a `docs/prompts/*.md` file

Steps 4 and 7 below are done by hand, using `docs/prompts/setup-cmux-workspaces.md` and `docs/prompts/run-dashboard-in-pane.md`. These are **not** scripts and there is no CLI command that runs them — each is a markdown file containing one block of instructions meant to be pasted, as-is, into an active Claude Code session:

1. Open cmux and start (or switch to) a Claude Code session in the workspace you intend to become **main** — the one the director and the dashboard will live in. `scaffold.sh` itself never opens or touches cmux, so this session is something you start yourself, after scaffolding finishes.
2. Open the prompt file in your scaffolded project (`docs/prompts/setup-cmux-workspaces.md` or `docs/prompts/run-dashboard-in-pane.md`) and copy everything inside the fenced code block under its own `## The prompt` heading — not the surrounding explanation, just that block.
3. Paste it as a message to that Claude Code session. It then runs the real `cmux` and shell commands itself, since it has an actual terminal and an actual cmux socket to talk to — a plain assistant session with no cmux underneath it (e.g. one running outside cmux entirely) cannot execute these for you.
4. Run `setup-cmux-workspaces.md` first (step 4) — it produces `.specify/cmux-workspaces.json`. Run `run-dashboard-in-pane.md` afterward (step 7), in the same or a new session, still inside main — it opens a `cmux new-split` and starts the dashboard inside it.

Both prompts state their own caveats and ask you to report back what actually happened the first time you run them for real — neither has been exercised against a live cmux instance as part of this template's own test suite (see the Status section in the top-level README).

## Scaffolding into an existing project

`--target` doesn't have to be an empty or new directory — point it at an existing repository's root to add this pipeline to a codebase you already have. Existing files, git history, and `.git/` are left alone; the scaffold only adds `.claude/skills-pipeline-roles/`, `.specify/`, `dashboard/`, `docs/`, and `specs/`.

**Safety check, not a suggestion.** If the target already has a non-empty `dashboard/` or `docs/` directory — common names an existing project might already own — `scaffold.sh` refuses to run rather than silently deleting and replacing them (an earlier version of this script did exactly that unconditionally; fixed once the risk was noticed, not after it caused real data loss). If you hit this:
- Move or rename your existing `dashboard/`/`docs/` directory before scaffolding, then move its contents back in afterward and resolve any real overlap by hand, or
- Scaffold into a subdirectory of your project instead of the root, or
- Open an issue if neither of those fits your situation — the check is deliberately conservative and may be worth relaxing for specific cases once there's a real one to design around.

This check does not currently look for narrower conflicts (e.g., a single file your project happens to also have inside `.specify/` or `specs/`) — it's scoped to the two directory names most likely to collide, not an exhaustive existing-file scan.

## What happens, step by step

1. **Git init** the target repository.
2. **Skills copied** into `.claude/skills/` — the 11 role skills, pulled and pinned, never hand-authored per project.
3. **`specify init . --integration claude`** — installs Spec Kit's own 6 skills and creates `.specify/memory/`, `.specify/scripts/`, `.specify/templates/`.
4. **Stand up the 3 core cmux workspaces** — main, design, implementation. (Review/docs/PR workspaces can be created lazily on first use.) Two ways to do this, same result: paste `docs/prompts/setup-cmux-workspaces.md`'s prompt into a Claude Code session running inside cmux (see "How to run a `docs/prompts/*.md` file," above), or run the equivalent `cmux` commands yourself following `docs/manual-cmux-workspace-setup.md`. cmux's CLI has no workspace-naming flag, so either path writes `.specify/cmux-workspaces.json`, the name→ID mapping the director skill reads to actually address these workspaces by `--workspace <id>` instead of a name cmux doesn't understand.
5. **Author `constitution.md`** from the rendered template — every `<<FILL:...>>` marker is a value only you can set: the triage rubric's module-boundary definition, both concurrency caps (per-feature and project-wide), both budget figures, the Opus-share ceiling percentage, and any project-specific sensitive surfaces. `scaffold.sh` refuses to consider scaffolding complete while any marker remains.
6. **Initialize `factory-log.md`** — the constitution's own creation becomes entry zero, logged, not treated as pre-log setup.
7. **Stand up the dashboard** — `dashboard/` is already copied by `scaffold.sh`; paste `docs/prompts/run-dashboard-in-pane.md`'s prompt into a Claude Code session in your main workspace (same mechanism as step 4, above) to generate `config.json`, start the backend, and confirm the frontend renders, all in a new pane alongside the director. See `docs/running-the-dashboard.md` for what that prompt actually runs, or to run those commands by hand outside cmux entirely.
8. **Dry-run one deliberately trivial synthetic feature** through all 9 gates by hand, approving explicitly at every gate. This is a genuine confidence check, not a formality — `scaffold.sh` does not automate this step on purpose.
9. **Recalibrate** the concurrency caps and budget figures using what the dry run actually logged. A fresh scaffold's caps are a starting guess.

## Definition of "ready for the first real feature"

- [ ] All 11 role skills present under `.claude/skills-pipeline-roles/`, loading without error.
- [ ] Spec Kit's own skills present under `.claude/skills/` (confirmed against a real `specify init`: 10 skills — `speckit-constitution`, `speckit-specify`, `speckit-clarify`, `speckit-plan`, `speckit-tasks`, `speckit-analyze`, `speckit-checklist`, `speckit-implement`, `speckit-converge`, `speckit-taskstoissues` — the exact set may change with the Spec Kit version you install; this repository doesn't control or vendor it).
- [ ] `constitution.md` structurally complete — no `<<FILL:...>>` markers remain.
- [ ] `factory-log.md` exists, structured-entry format from entry zero, documenting the constitution's own creation.
- [ ] The three core cmux workspaces exist and are reachable, and `.specify/cmux-workspaces.json` correctly maps `main`/`design`/`implementation` to their real IDs.
- [ ] The dashboard's backend is running and smoke-tested; the frontend renders correctly against the near-empty state.
- [ ] `docs/` present with all 9 files.
- [ ] One synthetic dry-run feature has completed all 9 gates, every gate approved explicitly by a human.
- [ ] Concurrency caps and budget figures have been revisited at least once using the dry run's own data.

Treat this list as a gate in its own right. A repository missing any item is still mid-scaffold, no matter how complete it feels.

## Updating an existing project

```bash
scaffold/scaffold.sh --sync --template-version <new-tag> --target ./my-project
```

Always explicit, never automatic. Skills, dashboard, and docs are safe to overwrite wholesale — provided you've never hand-edited them in place (if you have, that's a local fork, and sync will silently clobber it; fix upstream in the template instead). `constitution.md` is never wholesale-overwritten — only new required sections get added as flagged placeholders, your filled-in values are preserved. `factory-log.md` is never touched. Read the CHANGELOG for what's actually changing before syncing.
