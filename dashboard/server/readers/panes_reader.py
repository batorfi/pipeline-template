"""GET /panes's data layer — implements BE-020, BE-021.

Confirmed against a live cmux instance (2026-07-31), after the original
implementation was found completely broken during a real dry-run feature:
the director spawned multiple real panes across design/implementation
workspaces, but /panes always reported none. Root causes, all fixed here:

1. `cmux list-panels --json`'s real top-level key is "surfaces", not
   "panels" — the original code's `.get("panels", [])` fallback always
   returned an empty list against real output.
2. `list-panels` is scoped to whatever workspace the invoking process
   happens to be in — it needs an explicit `--workspace <id>` per call to
   see panes in a workspace other than the caller's own. Without the three
   IDs from .specify/cmux-workspaces.json, the backend could only ever see
   its own workspace, never design/implementation where the director
   actually works.
3. Real surfaces have no "status" field at all (no "running"/"idle"
   concept cmux exposes) — every real terminal/agentSession surface is
   now reported with status "running", the closest honest approximation
   available: if cmux currently has it open, something is likely
   happening in it. There's genuinely no way yet to distinguish "actively
   computing" from "idle, waiting for input" from cmux's own data.

`list-pane-surfaces` — a second command the original code also called —
was never actually observed to add anything beyond what `list-panels`
itself already returns (which, confusingly, is itself surface-level data,
not a separate "panel" concept); dropped rather than kept unconfirmed.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

PING_TIMEOUT_SECONDS = 2
LIST_TIMEOUT_SECONDS = 5

# Surface types that represent an actual running process worth showing as a
# "live pane" — confirmed real types also include "markdown" (an open file
# preview tab) and "browser" (the dashboard's own tab, most commonly),
# neither of which is pipeline work happening.
ACTIVE_SURFACE_TYPES = {"terminal", "agentSession"}


def _run_cmux(args: list[str], timeout: float, socket_path: str | None) -> subprocess.CompletedProcess:
    env = None
    if socket_path:
        import os

        env = {**os.environ, "CMUX_SOCKET_PATH": socket_path}
    return subprocess.run(
        ["cmux", *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
        check=False,
    )


def _panes_for_workspace(label: str, workspace_id: str, socket_path: str | None) -> list[dict[str, Any]]:
    args = ["list-panels", "--json"]
    if workspace_id:
        args += ["--workspace", workspace_id]
    proc = _run_cmux(args, LIST_TIMEOUT_SECONDS, socket_path)
    if proc.returncode != 0:
        return []

    try:
        data = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return []

    surfaces = data.get("surfaces", []) if isinstance(data, dict) else []

    # Group by pane_ref (a pane can have multiple surfaces/tabs open — e.g.
    # a terminal tab plus several markdown preview tabs sharing one pane).
    # Report one entry per pane, preferring the tab actually selected in it,
    # among the types that represent real work.
    by_pane: dict[str, dict[str, Any]] = {}
    for s in surfaces:
        if s.get("type") not in ACTIVE_SURFACE_TYPES:
            continue
        pane_ref = s.get("pane_ref")
        if not pane_ref:
            continue
        existing = by_pane.get(pane_ref)
        if existing is None or s.get("selected_in_pane"):
            by_pane[pane_ref] = s

    panes = []
    for pane_ref, s in by_pane.items():
        resume_binding = s.get("resume_binding") or {}
        panes.append(
            {
                "workspace": label,
                "pane_id": pane_ref,
                "role": None,  # not a documented cmux field — no reliable signal
                # observed yet for which pipeline role (researcher/worker/etc.)
                # a pane belongs to; title is the best available proxy.
                "status": "running",  # cmux exposes no running/idle distinction;
                # this reflects "cmux currently has this pane open," not
                # confirmed active computation — see module docstring.
                "current_task": s.get("title"),
                "is_claude_session": resume_binding.get("kind") == "claude",
            }
        )
    return panes


def read_panes(workspace_ids: dict[str, str] | None = None, socket_path: str | None = None) -> dict[str, Any]:
    """BE-021: bounded timeout, panes_unavailable flag on any failure — never hangs."""
    try:
        ping = _run_cmux(["ping"], PING_TIMEOUT_SECONDS, socket_path)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return {"panes": [], "panes_unavailable": True}

    if ping.returncode != 0:
        return {"panes": [], "panes_unavailable": True}

    if not workspace_ids:
        # No .specify/cmux-workspaces.json — fall back to whatever workspace
        # the backend's own process happens to be in, the pre-fix behavior,
        # rather than reporting unavailable when cmux itself is reachable.
        try:
            return {"panes": _panes_for_workspace("unknown", "", socket_path), "panes_unavailable": False}
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            return {"panes": [], "panes_unavailable": True}

    all_panes: list[dict[str, Any]] = []
    try:
        for label, workspace_id in workspace_ids.items():
            all_panes.extend(_panes_for_workspace(label, workspace_id, socket_path))
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return {"panes": [], "panes_unavailable": True}

    return {"panes": all_panes, "panes_unavailable": False}
