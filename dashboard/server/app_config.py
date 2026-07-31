"""Loads dashboard/config.json (per dashboard/config.schema.json) and resolves paths.

Read once at startup, held as app state — not re-read per request, since the
config file itself doesn't change during a running session (a project rename
or move would restart the backend anyway).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DashboardConfig:
    project_root: Path
    factory_log_path: Path
    tasks_path: Path | None
    constitution_path: Path
    cmux_socket_path: str | None
    cmux_workspace_ids: dict[str, str] | None

    def resolve_tasks_path(self) -> Path | None:
        """The configured tasks_path is a static value set once at scaffold
        time (dashboard/config.json), but Spec Kit creates each feature's
        tasks.md under a numbered per-feature directory
        (specs/<NNN-feature-slug>/tasks.md) that doesn't exist yet at
        scaffold time and changes with every new feature — a static path can
        never stay correct. If the configured path exists, honor it (a human
        may have pointed it somewhere deliberately); otherwise fall back to
        the most recently modified specs/*/tasks.md, a reasonable proxy for
        "the feature currently being worked."
        """
        if self.tasks_path is not None and self.tasks_path.exists():
            return self.tasks_path

        candidates = list((self.project_root / "specs").glob("*/tasks.md"))
        if not candidates:
            return None
        return max(candidates, key=lambda p: p.stat().st_mtime)

    @classmethod
    def load(cls, config_json_path: str | Path, project_root: str | Path | None = None) -> "DashboardConfig":
        # Resolve to an absolute path BEFORE computing .parent.parent — pathlib's
        # .parent is purely lexical, so a bare relative filename like "config.json"
        # (no directory component) has parent "." whose own .parent is ALSO "."
        # (there's no syntactic "above" a lexical "."), silently collapsing
        # project_root to the wrong directory. .resolve() first makes .parent
        # actually walk up real filesystem directories.
        config_json_path = Path(config_json_path).resolve()
        with open(config_json_path, encoding="utf-8") as fh:
            data = json.load(fh)

        for required in ("factory_log_path", "tasks_path", "constitution_path"):
            if required not in data:
                raise ValueError(f"dashboard config missing required field: {required}")

        root = Path(project_root).resolve() if project_root else config_json_path.parent.parent

        tasks_path = root / data["tasks_path"]

        # .specify/cmux-workspaces.json holds the main/design/implementation
        # name->ID mapping (docs/manual-cmux-workspace-setup.md /
        # setup-cmux-workspaces.sh). /panes needs these IDs to query the
        # actual workspaces the director spawns real panes into — without
        # them, cmux list-panels only ever sees whatever workspace the
        # dashboard backend's own process happens to be running in, which is
        # very often none of the three that actually matter.
        cmux_workspaces_path = root / ".specify" / "cmux-workspaces.json"
        cmux_workspace_ids: dict[str, str] | None = None
        if cmux_workspaces_path.exists():
            try:
                with open(cmux_workspaces_path, encoding="utf-8") as fh:
                    cmux_workspace_ids = json.load(fh)
            except (json.JSONDecodeError, OSError):
                cmux_workspace_ids = None

        return cls(
            project_root=root,
            factory_log_path=root / data["factory_log_path"],
            tasks_path=tasks_path if tasks_path else None,
            constitution_path=root / data["constitution_path"],
            cmux_socket_path=data.get("cmux_socket_path") or os.environ.get("CMUX_SOCKET_PATH"),
            cmux_workspace_ids=cmux_workspace_ids,
        )
