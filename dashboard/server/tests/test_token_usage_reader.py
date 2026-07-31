"""read_token_usage(): real per-pane token consumption, sourced from a
Claude Code pane's own local session transcript (~/.claude/projects/<slug>/
<session-id>.jsonl), keyed by resume_binding.checkpoint_id. Investigated in
response to a real question about $0.00 showing everywhere on the
dashboard -- cmux itself exposes no usage/cost/token data of any kind, but
Claude Code's own local transcripts do, confirmed against a real transcript
from a real dry-run feature.
"""

from __future__ import annotations

import json

from dashboard.server.readers.token_usage_reader import read_token_usage


def _transcript_line(input_tokens: int, output_tokens: int, **extra_usage) -> str:
    usage = {"input_tokens": input_tokens, "output_tokens": output_tokens, **extra_usage}
    return json.dumps({"type": "assistant", "message": {"usage": usage}})


def test_sums_usage_across_a_real_shaped_transcript(tmp_path):
    project_dir = tmp_path / "-Users-someone-repos-my-project"
    project_dir.mkdir()
    transcript = project_dir / "session-abc.jsonl"
    transcript.write_text(
        "\n".join(
            [
                _transcript_line(2, 194, cache_creation_input_tokens=39939, cache_read_input_tokens=0),
                _transcript_line(1200, 340, cache_creation_input_tokens=0, cache_read_input_tokens=39939),
                json.dumps({"type": "user", "message": {"content": "no usage on user turns"}}),
            ]
        ),
        encoding="utf-8",
    )

    result = read_token_usage("session-abc", claude_projects_dir=tmp_path)

    assert result["available"] is True
    assert result["input_tokens"] == 1202
    assert result["output_tokens"] == 534
    assert result["total_tokens"] == 1736
    assert result["cache_creation_input_tokens"] == 39939
    assert result["cache_read_input_tokens"] == 39939


def test_unavailable_when_transcript_not_found(tmp_path):
    result = read_token_usage("does-not-exist-session", claude_projects_dir=tmp_path)
    assert result == {"available": False}


def test_tolerant_of_malformed_lines(tmp_path):
    project_dir = tmp_path / "-Users-someone-repos-my-project"
    project_dir.mkdir()
    transcript = project_dir / "session-xyz.jsonl"
    transcript.write_text(
        "\n".join(["not valid json at all", "", _transcript_line(10, 5)]),
        encoding="utf-8",
    )

    result = read_token_usage("session-xyz", claude_projects_dir=tmp_path)

    assert result["available"] is True
    assert result["input_tokens"] == 10
    assert result["output_tokens"] == 5


def test_searches_across_all_project_subdirectories(tmp_path):
    """A pane's session transcript could live under any project directory
    (cwd-slug), not necessarily the current project's own -- glob across
    all of them by session ID, which is unique regardless of path."""
    other_project = tmp_path / "-Users-someone-repos-some-other-project"
    other_project.mkdir()
    (other_project / "session-elsewhere.jsonl").write_text(_transcript_line(7, 3), encoding="utf-8")

    result = read_token_usage("session-elsewhere", claude_projects_dir=tmp_path)

    assert result["available"] is True
    assert result["input_tokens"] == 7
