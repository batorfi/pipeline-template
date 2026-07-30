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

This mechanizes steps 1–7 below in one command: clones this template repo at the pinned tag (plain `git clone`, or `gh repo clone` if `gh` happens to be installed — neither requires auth against a public repo), git-inits the target if needed, copies skills/dashboard/docs/specs-README, renders `constitution.template.md` and the factory-log templates, and runs `specify init`.

## What happens, step by step

1. **Git init** the target repository.
2. **Skills copied** into `.claude/skills/` — the 11 role skills, pulled and pinned, never hand-authored per project.
3. **`specify init . --integration claude`** — installs Spec Kit's own 6 skills and creates `.specify/memory/`, `.specify/scripts/`, `.specify/templates/`.
4. **Stand up the 3 core cmux workspaces** — main, design, implementation. (Review/docs/PR workspaces can be created lazily on first use.)
5. **Author `constitution.md`** from the rendered template — every `<<FILL:...>>` marker is a value only you can set: the triage rubric's module-boundary definition, both concurrency caps (per-feature and project-wide), both budget figures, the Opus-share ceiling percentage, and any project-specific sensitive surfaces. `scaffold.sh` refuses to consider scaffolding complete while any marker remains.
6. **Initialize `factory-log.md`** — the constitution's own creation becomes entry zero, logged, not treated as pre-log setup.
7. **Stand up the dashboard** — copy `dashboard/`, generate `config.json` with real paths, start the backend, confirm the frontend renders. See `docs/running-the-dashboard.md`.
8. **Dry-run one deliberately trivial synthetic feature** through all 9 gates by hand, approving explicitly at every gate. This is a genuine confidence check, not a formality — `scaffold.sh` does not automate this step on purpose.
9. **Recalibrate** the concurrency caps and budget figures using what the dry run actually logged. A fresh scaffold's caps are a starting guess.

## Definition of "ready for the first real feature"

- [ ] All 11 role skills and all 6 Spec Kit skills present under `.claude/skills/`, loading without error.
- [ ] `constitution.md` structurally complete — no `<<FILL:...>>` markers remain.
- [ ] `factory-log.md` exists, structured-entry format from entry zero, documenting the constitution's own creation.
- [ ] The three core cmux workspaces exist and are reachable.
- [ ] The dashboard's backend is running and smoke-tested; the frontend renders correctly against the near-empty state.
- [ ] `docs/` present with all 7 files.
- [ ] One synthetic dry-run feature has completed all 9 gates, every gate approved explicitly by a human.
- [ ] Concurrency caps and budget figures have been revisited at least once using the dry run's own data.

Treat this list as a gate in its own right. A repository missing any item is still mid-scaffold, no matter how complete it feels.

## Updating an existing project

```bash
scaffold/scaffold.sh --sync --template-version <new-tag> --target ./my-project
```

Always explicit, never automatic. Skills, dashboard, and docs are safe to overwrite wholesale — provided you've never hand-edited them in place (if you have, that's a local fork, and sync will silently clobber it; fix upstream in the template instead). `constitution.md` is never wholesale-overwritten — only new required sections get added as flagged placeholders, your filled-in values are preserved. `factory-log.md` is never touched. Read the CHANGELOG for what's actually changing before syncing.
