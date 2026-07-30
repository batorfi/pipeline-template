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
        return cls(
            project_root=root,
            factory_log_path=root / data["factory_log_path"],
            tasks_path=tasks_path if tasks_path else None,
            constitution_path=root / data["constitution_path"],
            cmux_socket_path=data.get("cmux_socket_path") or os.environ.get("CMUX_SOCKET_PATH"),
        )
