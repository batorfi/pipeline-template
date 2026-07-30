"""Implements BE-AC1 (log portion): all-stages-valid, one-malformed-entry, header-only-empty."""

from pathlib import Path

from dashboard.server.readers.log_reader import read_log


def test_all_stages_valid(pipeline_root):
    result = read_log(pipeline_root / "factory-log/fixtures/all-stages-valid.md")
    assert result["errors"] == []
    assert len(result["entries"]) == 15
    # newest-first
    assert result["entries"][0]["stage"] == "pr_gate"
    assert result["entries"][-1]["stage"] == "constitution"


def test_one_malformed_entry_isolated(pipeline_root):
    result = read_log(pipeline_root / "factory-log/fixtures/one-malformed-entry.md")
    assert len(result["errors"]) == 7
    # the malformed entry is dropped from `entries`, but its 4 well-formed
    # siblings still parse
    assert len(result["entries"]) == 4


def test_header_only_empty_is_valid(pipeline_root):
    result = read_log(pipeline_root / "factory-log/fixtures/header-only-empty.md")
    assert result["errors"] == []
    assert result["entries"] == []


def test_missing_file_is_valid_empty(pipeline_root):
    result = read_log(pipeline_root / "factory-log/fixtures/does-not-exist.md")
    assert result == {"entries": [], "errors": []}


def test_feature_filter(pipeline_root):
    result = read_log(pipeline_root / "factory-log/fixtures/all-stages-valid.md", feature="001-rate-limit-middleware")
    # constitution entry has no `feature` field (LOG-011) and is correctly excluded
    assert all(e.get("feature") == "001-rate-limit-middleware" for e in result["entries"])
    assert len(result["entries"]) == 14


def test_limit(pipeline_root):
    result = read_log(pipeline_root / "factory-log/fixtures/all-stages-valid.md", limit=3)
    assert len(result["entries"]) == 3


def test_entries_carry_prose_summary(pipeline_root):
    """The dashboard's step-report feed needs each entry's plain-language
    prose, not just its frontmatter — validator.py synthesizes a `summary`
    key from the prose body for exactly this reason."""
    result = read_log(pipeline_root / "factory-log/fixtures/all-stages-valid.md")
    assert all(e.get("summary") for e in result["entries"])
    pr_gate_entry = next(e for e in result["entries"] if e["stage"] == "pr_gate")
    assert "MR opened" in pr_gate_entry["summary"]
