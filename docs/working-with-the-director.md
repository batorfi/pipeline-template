# Working with the director

The mechanics of actually running a feature through this pipeline — starting the director, handing it work, and responding at a gate. `docs/human-gates.md` covers *what each gate is asking*; `docs/workflow-overview.md` covers the roles and stage sequence; this doc covers the part neither of those does: what you actually type, where, and what to expect back.

## What the director is, concretely

The director isn't a separate program — it's a Claude Code session, running in your project's **main** cmux workspace, with the `director` skill (`.claude/skills-pipeline-roles/director/SKILL.md`) loaded. You talk to it the same way you'd talk to any Claude Code session: plain messages in that session's chat. There's no separate director UI or CLI.

**The dashboard is not that session.** It's a separate, read-only FastAPI + vanilla-JS app that reads `factory-log.md`, `tasks.md`, and `constitution.md` and renders their current state — attention band, live panes, step reports, task board, totals. It never writes to any of those files, never sends a decision anywhere, and has no button wired to actually do anything (see the note on this below). If you're looking at the dashboard and something needs your input, you still give that input in the director's chat, not in the browser tab.

## Starting a feature

1. Confirm you're in a Claude Code session in **main**, with the director skill available (it's under `.claude/skills-pipeline-roles/director/` — reference it explicitly if your session doesn't pick it up automatically, e.g. "use the director skill to start a feature").
2. Confirm the director's own startup checklist is satisfied first — it checks this itself, but you can pre-empt: `.specify/` exists, `constitution.md` has no remaining `<<FILL:...>>` markers, `.specify/factory-log.md` exists, and `.specify/cmux-workspaces.json` has real `main`/`design`/`implementation` IDs (from whichever cmux-workspace-setup doc you used).
3. Hand it a raw idea — a sentence, a paragraph, a pasted ticket, whatever you have. For your first dry run, keep it deliberately trivial (per `docs/scaffolding-guide.md` step 8) — something like "add a `--version` flag to `scripts/hello.py` that prints the current version and exits."
4. The director triages it (small vs. standard), tells you which, and — for standard features — spawns the researcher pane in the design workspace before anything else. You'll see this reflected in the dashboard's live-panes zone and step-report feed shortly after, since the director logs each stage transition as it happens.

## Responding at a gate

When the director reaches a gate, it stops and presents what's ready — the relevant artifact(s), summarized in plain language, per `docs/human-gates.md`'s entry for that specific gate. It will not proceed until you respond. Read the artifact it points you to (not just its summary) before deciding.

Respond in the same chat, in plain language — there's no fixed command syntax, but the moves each gate accepts are always one of:
- **"Approve"** (or similar) — moves to the next stage.
- **"Revise: <feedback>"** — sends your feedback back to the pane that produced the artifact, which retries.
- **"Reject"** — stops the feature here (only valid on gates that list reject as a move — see `docs/human-gates.md`).
- **"Restart"** — review gate only; carries the review report all the way back to triage.

The director logs your decision (and any feedback) to `factory-log.md` as part of that gate's entry once you respond — this is what the dashboard's step-report feed and attention band pick up and display afterward. There's a real, if usually short, lag between you approving and the dashboard showing it, since the dashboard only reflects what's already been logged.

## What the dashboard is actually for, in this flow

Use it to watch, not to act:
- **Attention band** — at a glance, whether anything is waiting on you right now, without needing to switch to the director's pane to check.
- **Live panes** — which ephemeral panes are currently running, in which workspace.
- **Step reports** — the plain-language history of what's happened so far on the current feature.
- **Task board + totals** — implementation-phase task status and running spend, once fan-out has started.

If the dashboard shows a gate is open but you don't have the director's chat handy, switch to the main workspace and respond there — the dashboard has no way to accept your decision itself.

## If something looks stuck

- **Dashboard shows an open gate, nothing happening.** Normal — the director is waiting on you. Go respond in its chat.
- **You typed a decision but the dashboard hasn't updated.** Give it a moment (the director logs after you respond, the dashboard reads on its own refresh cycle); if it's been a while, check the director's chat directly for whether it actually received and processed your message.
- **The director seems to have skipped a gate.** This should not happen — gates are non-negotiable per the skill's own stated boundaries. If you see it, that's a real bug in that session's behavior; check `factory-log.md` directly for what was actually logged, and treat it as something to report, not something to work around by manually editing the log.
- **You closed the session / came back later.** The director isn't stateful in memory beyond the chat itself — `factory-log.md` is the actual source of truth for where a feature stands. Starting a fresh Claude Code session with the director skill in main and asking it to resume the current feature should let it re-orient from the log.

## Consumers of what you approve

Everything you approve becomes an entry in `.specify/factory-log.md`, which is also what a later feature's triage rubric and tier assignments get recalibrated against (`docs/scaffolding-guide.md` step 9) — your gate decisions aren't just moving the current feature forward, they're the data this whole system uses to get its own defaults right over time.
