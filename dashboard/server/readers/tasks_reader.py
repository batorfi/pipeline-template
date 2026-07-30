"""GET /tasks's data layer — implements BE-010.

Parses a Spec Kit tasks.md into {id, parallel, story, file_path, checked, phase}
objects grouped by phase. Tolerant of tasks.md's actual format varying slightly
(this is Spec Kit's own artifact, not something this pipeline controls the
exact formatting of) — a task line that doesn't match the expected shape is
skipped rather than crashing the whole parse.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

PHASE_HEADING_RE = re.compile(r"^#{2,3}\s+(.*)$")
TASK_LINE_RE = re.compile(
    r"^- \[(?P<checked>[ xX])\]\s+"
    r"(?P<id>\S+)\s+"
    r"(?:\[P\]\s+)?"
    r"(?:\[(?P<story>[^\]]+)\]\s+)?"
    r"(?P<description>.*)$"
)
FILE_PATH_HINT_RE = re.compile(r"(\S+/\S+)")


def read_tasks(path: Path | None) -> dict[str, Any]:
    """BE-AC3: an absent or empty tasks.md is a valid fresh-scaffold state, not an error."""
    if path is None or not path.exists():
        return {"phases": []}

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    phases: list[dict[str, Any]] = []
    current_phase: dict[str, Any] | None = None

    for line in lines:
        heading = PHASE_HEADING_RE.match(line)
        if heading:
            current_phase = {"phase": heading.group(1).strip(), "tasks": []}
            phases.append(current_phase)
            continue

        task_match = TASK_LINE_RE.match(line)
        if task_match and current_phase is not None:
            description = task_match.group("description").strip()
            file_hint = FILE_PATH_HINT_RE.search(description)
            current_phase["tasks"].append(
                {
                    "id": task_match.group("id"),
                    "parallel": "[P]" in line,
                    "story": task_match.group("story"),
                    "file_path": file_hint.group(1) if file_hint else None,
                    "checked": task_match.group("checked").lower() == "x",
                    "description": description,
                }
            )

    return {"phases": phases}
