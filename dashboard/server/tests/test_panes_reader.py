"""read_panes(): a real dry-run feature found this completely broken --
the director spawned multiple real panes across design/implementation
workspaces, but /panes always reported none. Fixtures below use the exact
response shape confirmed against a live cmux instance (2026-07-31): a
"surfaces" list (not "panels"), scoped per --workspace call.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

from dashboard.server.readers.panes_reader import read_panes


def _surface(**kwargs) -> dict[str, Any]:
    base = {
        "focused": False,
        "index": 0,
        "index_in_pane": 0,
        "pane_ref": "pane:1",
        "ref": "surface:1",
        "selected_in_pane": True,
        "title": "some title",
        "type": "terminal",
    }
    base.update(kwargs)
    return base


def _list_panels_result(surfaces: list[dict[str, Any]], workspace_ref: str) -> subprocess.CompletedProcess:
    payload = {"surfaces": surfaces, "window_ref": "window:1", "workspace_ref": workspace_ref}
    return subprocess.CompletedProcess(args=[], returncode=0, stdout=json.dumps(payload), stderr="")


def _ping_ok() -> subprocess.CompletedProcess:
    return subprocess.CompletedProcess(args=[], returncode=0, stdout="PONG\n", stderr="")


def test_real_response_shape_parses_correctly(monkeypatch):
    """The exact bug: real cmux output keys panes under "surfaces", not
    "panels" -- the original implementation always returned an empty list
    against this real shape."""
    calls: list[list[str]] = []

    def fake_run(args, **kwargs):
        calls.append(args)
        if args[1] == "ping":
            return _ping_ok()
        surfaces = [
            _surface(pane_ref="pane:27", ref="surface:39", title="✳ Claude Code", type="terminal",
                     resume_binding={"kind": "claude"}),
            _surface(pane_ref="pane:27", ref="surface:40", title="Claude Code · React",
                     type="agentSession", selected_in_pane=False),
            _surface(pane_ref="pane:20", ref="surface:55", title="verification.md", type="markdown"),
        ]
        return _list_panels_result(surfaces, "workspace:19")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = read_panes(workspace_ids={"design": "workspace:19"})

    assert result["panes_unavailable"] is False
    # One pane (pane:27) counted once, deduplicated by pane_ref; the
    # markdown-type surface on pane:20 is excluded (not real running work).
    assert len(result["panes"]) == 1
    pane = result["panes"][0]
    assert pane["workspace"] == "design"
    assert pane["pane_id"] == "pane:27"
    assert pane["current_task"] == "✳ Claude Code"
    assert pane["status"] == "running"
    assert pane["is_claude_session"] is True
    assert pane["tokens"] is None  # resume_binding has no checkpoint_id here


def test_queries_each_configured_workspace_with_explicit_flag(monkeypatch):
    """Without --workspace, list-panels only ever sees the caller's own
    workspace -- confirmed bug #2. Each configured workspace must get its
    own explicit --workspace call."""
    seen_workspace_flags = []

    def fake_run(args, **kwargs):
        if args[1] == "ping":
            return _ping_ok()
        if "--workspace" in args:
            seen_workspace_flags.append(args[args.index("--workspace") + 1])
        return _list_panels_result([], "workspace:x")

    monkeypatch.setattr(subprocess, "run", fake_run)

    read_panes(workspace_ids={"main": "workspace:15", "design": "workspace:19", "implementation": "workspace:20"})

    assert set(seen_workspace_flags) == {"workspace:15", "workspace:19", "workspace:20"}


def test_no_workspace_ids_falls_back_to_unscoped_call(monkeypatch):
    def fake_run(args, **kwargs):
        if args[1] == "ping":
            return _ping_ok()
        assert "--workspace" not in args
        return _list_panels_result([_surface()], "workspace:1")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = read_panes(workspace_ids=None)

    assert result["panes_unavailable"] is False
    assert len(result["panes"]) == 1
    assert result["panes"][0]["workspace"] == "unknown"


def test_ping_failure_reports_unavailable(monkeypatch):
    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="not running")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = read_panes(workspace_ids={"main": "workspace:15"})

    assert result == {"panes": [], "panes_unavailable": True}


def test_claude_session_pane_gets_real_token_usage(monkeypatch):
    """A pane with a real checkpoint_id gets real token data attached, read
    via token_usage_reader.read_token_usage -- not the previous permanent
    $0.00-equivalent placeholder."""
    from dashboard.server.readers import panes_reader

    def fake_run(args, **kwargs):
        if args[1] == "ping":
            return _ping_ok()
        surfaces = [
            _surface(
                pane_ref="pane:27",
                title="✳ Claude Code",
                resume_binding={"kind": "claude", "checkpoint_id": "session-real-123"},
            ),
        ]
        return _list_panels_result(surfaces, "workspace:19")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        panes_reader,
        "read_token_usage",
        lambda session_id: {"available": True, "total_tokens": 4200} if session_id == "session-real-123" else None,
    )

    result = read_panes(workspace_ids={"design": "workspace:19"})

    assert result["panes"][0]["tokens"] == {"available": True, "total_tokens": 4200}


def test_markdown_and_browser_surfaces_excluded(monkeypatch):
    """Only terminal/agentSession surfaces represent real pipeline work --
    open file previews and the dashboard's own browser tab are not panes."""

    def fake_run(args, **kwargs):
        if args[1] == "ping":
            return _ping_ok()
        surfaces = [
            _surface(pane_ref="pane:26", type="markdown", title="plan.md"),
            _surface(pane_ref="pane:26", type="browser", title="Pipeline Dashboard"),
        ]
        return _list_panels_result(surfaces, "workspace:15")

    monkeypatch.setattr(subprocess, "run", fake_run)

    result = read_panes(workspace_ids={"main": "workspace:15"})

    assert result["panes"] == []
    assert result["panes_unavailable"] is False
