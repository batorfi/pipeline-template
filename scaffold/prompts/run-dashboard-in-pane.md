# Prompt: run the dashboard in a side pane of the main workspace

Paste this into the Claude Code session already running in your **main** workspace (the same workspace named per `docs/manual-cmux-workspace-setup.md`, where the director will live). This implements scaffold step 3 / T069 — "start the dashboard backend and confirm the frontend renders."

Per the pipeline concept, the main workspace holds exactly two things: the director pane and the dashboard, side by side, and nothing else is ever spawned into it. This prompt creates that second pane and starts the dashboard in it.

---

## The prompt

```
Start the dashboard in a new side pane of this (main) workspace, per
docs/running-the-dashboard.md.

1. Split this workspace to create a new pane for the dashboard:
   cmux new-split right
   (Use `--workspace <main-id>` from .specify/cmux-workspaces.json if this
   command doesn't default to the current workspace — confirm against your
   actual cmux CLI behavior.)

2. Identify the new pane so you can target it:
   cmux list-panels --json
   Find the pane that wasn't there before this split.

3. In that new pane, generate dashboard/config.json if it doesn't already
   exist, pointing at this project's real paths:
   {
     "factory_log_path": "../.specify/factory-log.md",
     "tasks_path": "../specs/<current-feature>/tasks.md",
     "constitution_path": "../.specify/memory/constitution.md",
     "cmux_socket_path": null
   }
   (Adjust tasks_path once a feature actually exists — before the first
   feature's plan gate, point it at any nonexistent path; that's valid
   empty state, not an error.)

4. In that new pane, start the dashboard (backend + frontend, one process
   — see docs/running-the-dashboard.md for why this must be one process,
   not two):
   cd dashboard
   PIPELINE_CONFIG=config.json uv run --with fastapi --with uvicorn --with pyyaml python3 -c "
   from server.app import create_app
   from fastapi.staticfiles import StaticFiles
   app = create_app(config_path='config.json')
   app.mount('/', StaticFiles(directory='.', html=True), name='static')
   import uvicorn
   uvicorn.run(app, host='127.0.0.1', port=8000)
   "

5. Confirm it's actually serving, from any pane:
   curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/
   curl -s http://localhost:8000/log

6. Report back: the new pane's ID, confirmation the dashboard responded
   200, and whether /log returned the expected near-empty state
   ({"entries": [], "errors": []} on a fresh project).

Do not put the dashboard pane in any workspace other than main. Do not
spawn anything else into this workspace — it holds exactly the director
and the dashboard, per the pipeline design, nothing more.
```

---

## Caveat, stated plainly

This prompt was written from `docs/cmux/cli-reference.md` alone for the `cmux new-split`/`list-panels` portion — **not run against a live cmux instance** as part of this template's own build. The dashboard-starting command itself (steps 3-5) *is* fully verified — it's the exact single-process form confirmed working end to end in `dashboard/NOTES.md`. What's unconfirmed is only the cmux pane-mechanics wrapper around it: whether `cmux new-split` needs an explicit `--workspace` flag to target a non-current workspace, and whether the newly created pane is reliably identifiable from a `list-panels --json` diff. **Report back what you actually see** so this can be corrected.

## Keeping it running

This process holds the pane open (`uvicorn.run` blocks). If you need to restart it after a code or config change, `Ctrl-C` in that pane and re-run the same command — there's no `--reload` in the verified command above; add `--reload` yourself if you're actively iterating on the dashboard's own code, but drop it again for normal use (a silently-reloading dashboard process is one more thing that can behave unexpectedly mid-feature).
