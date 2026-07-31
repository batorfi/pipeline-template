"""Reads real per-pane token usage from local Claude Code session transcripts.

Investigated in response to a real question: the dashboard showed $0.00
everywhere because factory-log.md's usage blocks were always logged with a
hardcoded 0.0 placeholder -- cmux itself exposes no usage/cost/token command
of any kind (confirmed against its full `--help` command list). But a real
pane's `resume_binding.checkpoint_id` (when `resume_binding.kind ==
"claude"`, from list-panels --json) is the same UUID Claude Code uses to
name its own local session transcript, written to
~/.claude/projects/<project-dir-slug>/<checkpoint_id>.jsonl regardless of
this pipeline. Each assistant turn in that JSONL carries a real
message.usage block (input_tokens, output_tokens,
cache_creation_input_tokens, cache_read_input_tokens) -- confirmed by
inspecting a real transcript from a real dry-run feature's worker pane.
Summing these gives real, not-placeholder token consumption for that pane's
session.

This reads local files only, on the same machine the dashboard backend runs
on -- a pane resumed from a different machine (or a pruned/deleted
transcript) simply reports unavailable, same "never break the dashboard on
missing data" discipline as every other reader here.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _find_transcript(session_id: str, claude_projects_dir: Path) -> Path | None:
    matches = list(claude_projects_dir.glob(f"*/{session_id}.jsonl"))
    return matches[0] if matches else None


def read_token_usage(session_id: str, claude_projects_dir: Path | None = None) -> dict[str, Any]:
    """Sums real token usage across a Claude Code session's local transcript.

    Returns {"available": False} if the transcript can't be found -- never
    raises.
    """
    root = claude_projects_dir or (Path.home() / ".claude" / "projects")
    transcript = _find_transcript(session_id, root)
    if transcript is None:
        return {"available": False}

    input_tokens = 0
    output_tokens = 0
    cache_creation_tokens = 0
    cache_read_tokens = 0

    try:
        with open(transcript, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue
                usage = (record.get("message") or {}).get("usage")
                if not usage:
                    continue
                input_tokens += usage.get("input_tokens", 0) or 0
                output_tokens += usage.get("output_tokens", 0) or 0
                cache_creation_tokens += usage.get("cache_creation_input_tokens", 0) or 0
                cache_read_tokens += usage.get("cache_read_input_tokens", 0) or 0
    except OSError:
        return {"available": False}

    return {
        "available": True,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cache_creation_input_tokens": cache_creation_tokens,
        "cache_read_input_tokens": cache_read_tokens,
        "total_tokens": input_tokens + output_tokens,
    }
