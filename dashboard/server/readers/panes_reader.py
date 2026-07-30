"""GET /panes's data layer — implements BE-020, BE-021.

Commands confirmed against docs/cmux/cli-reference.md: `cmux ping` (liveness),
`cmux list-panels --json`, `cmux list-pane-surfaces --json`. The exact JSON
response shape from list-panels/list-pane-surfaces is NOT yet confirmed
against a live cmux instance (flagged in implementation-specs.md §7) — the
parsing below is a best-effort mapping and should be revisited once a live
instance is available to test against, per T024's tracked exception.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

PING_TIMEOUT_SECONDS = 2
LIST_TIMEOUT_SECONDS = 5


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


def read_panes(socket_path: str | None = None) -> dict[str, Any]:
    """BE-021: bounded timeout, panes_unavailable flag on any failure — never hangs."""
    try:
        ping = _run_cmux(["ping"], PING_TIMEOUT_SECONDS, socket_path)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return {"panes": [], "panes_unavailable": True}

    if ping.returncode != 0:
        return {"panes": [], "panes_unavailable": True}

    try:
        panels_proc = _run_cmux(["list-panels", "--json"], LIST_TIMEOUT_SECONDS, socket_path)
        surfaces_proc = _run_cmux(["list-pane-surfaces", "--json"], LIST_TIMEOUT_SECONDS, socket_path)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return {"panes": [], "panes_unavailable": True}

    if panels_proc.returncode != 0:
        return {"panes": [], "panes_unavailable": True}

    try:
        panels_data = json.loads(panels_proc.stdout or "[]")
    except json.JSONDecodeError:
        return {"panes": [], "panes_unavailable": True}

    surfaces_by_panel: dict[str, Any] = {}
    if surfaces_proc.returncode == 0:
        try:
            surfaces_data = json.loads(surfaces_proc.stdout or "[]")
            for s in surfaces_data if isinstance(surfaces_data, list) else []:
                panel_id = s.get("panelId") or s.get("panel_id") or s.get("id")
                if panel_id:
                    surfaces_by_panel[panel_id] = s
        except json.JSONDecodeError:
            pass  # surfaces are supplementary; a bad payload here doesn't fail the whole request

    panes = []
    raw_panels = panels_data if isinstance(panels_data, list) else panels_data.get("panels", [])
    for p in raw_panels:
        panel_id = p.get("id") or p.get("panelId")
        surface = surfaces_by_panel.get(panel_id, {})
        panes.append(
            {
                "workspace": p.get("workspace") or p.get("workspaceId"),
                "pane_id": panel_id,
                "role": surface.get("role"),  # not a documented cmux field — populated once a
                # convention for tagging a pane's pipeline role exists (e.g. via cmux set-status);
                # None until then, and the frontend must handle that (FE-AC2-style degradation).
                "status": p.get("status", "unknown"),
                "current_task": surface.get("currentTask") or surface.get("current_task"),
            }
        )

    return {"panes": panes, "panes_unavailable": False}
