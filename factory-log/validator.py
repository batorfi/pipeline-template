"""Validator for factory-log.md, per factory-log/SCHEMA.md (schema v1).

Implements LOG-001 through LOG-024. Used by:
- The dashboard backend's /log and /stats endpoints (parse-and-validate on read).
- scaffold.sh / CI, to check a log file conforms before trusting it.
- Ad hoc: `python validator.py path/to/factory-log.md`.

Design intent: a single malformed entry must not prevent parsing the entries
around it (LOG-AC2) — this module always returns everything it could parse,
plus a separate list of errors, rather than raising on the first problem.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from datetime import datetime

import yaml

SCHEMA_VERSION = "v1"

HEADER_RE = re.compile(r"^<!-- factory-log schema (v\d+) — see factory-log/SCHEMA\.md -->\s*$")

STAGE_VOCAB = {
    "constitution",
    "feature_init",
    "triage",
    "researcher",
    "concept_gate",
    "architecture_gate",
    "adr",
    "spec_gate",
    "plan_gate",
    "checkpoint_gate",
    "worker_task",
    "review_gate",
    "verification_gate",
    "docs_gate",
    "pr_gate",
}

# Stages considered "purely mechanical director actions" — exempt from the
# model-backed-pane fields required by LOG-020.
MECHANICAL_STAGES = {"constitution", "feature_init", "triage"}

VALID_TIERS = {"opus", "sonnet", "haiku"}
VALID_DECISIONS = {"approve", "revise", "reject", "restart", "mitigate", None}

BASE_REQUIRED_FIELDS = ("timestamp", "stage", "duration_seconds")
MODEL_BACKED_FIELDS = ("pane", "tier", "attempt", "escalated_from", "usage")
GATE_FIELDS = ("decision", "feedback")

STAGE_SPECIFIC_REQUIRED = {
    "checkpoint_gate": ("phase",),
    "worker_task": ("task_id", "parallel_group"),
    "verification_gate": ("story_id", "mitigation_round"),
    "triage": ("triage_result",),
}

VALID_TRIAGE_RESULTS = {"small", "standard"}


@dataclass
class ValidationError:
    entry_index: int  # 0-based position among parsed entries; -1 for file-level errors
    message: str

    def __str__(self) -> str:
        where = "file" if self.entry_index == -1 else f"entry #{self.entry_index}"
        return f"[{where}] {self.message}"


@dataclass
class ParseResult:
    entries: list[dict] = field(default_factory=list)
    errors: list[ValidationError] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _split_entries(text: str) -> tuple[str | None, list[str]]:
    """Split raw file text into (header_line, [raw frontmatter+prose blocks])."""
    lines = text.splitlines()
    if not lines:
        return None, []

    header = lines[0] if HEADER_RE.match(lines[0]) else None
    body = "\n".join(lines[1:]) if header is not None else text

    # Entries are `---\n<yaml>\n---\n<prose>` blocks, back to back.
    blocks: list[str] = []
    parts = body.split("---")
    # split on '---' yields: ['', yaml1, prose1+yaml2? ...] — walk pairwise instead.
    # Simpler and more robust: regex-match each frontmatter block explicitly.
    for m in re.finditer(r"^---\s*\n(.*?)\n---\s*\n(.*?)(?=(?:\n---\s*\n)|\Z)", body, re.DOTALL | re.MULTILINE):
        blocks.append(m.group(0))
    return header, blocks


def _validate_entry(raw_block: str, index: int) -> tuple[dict | None, list[ValidationError]]:
    errors: list[ValidationError] = []
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", raw_block, re.DOTALL)
    if not m:
        errors.append(ValidationError(index, "entry is not a well-formed frontmatter+prose block"))
        return None, errors

    yaml_text, prose = m.group(1), m.group(2)

    try:
        fm = yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError as e:
        errors.append(ValidationError(index, f"invalid YAML frontmatter: {e}"))
        return None, errors

    if not isinstance(fm, dict):
        errors.append(ValidationError(index, "frontmatter did not parse to a mapping"))
        return None, errors

    if not prose.strip():
        errors.append(ValidationError(index, "missing prose summary after frontmatter (LOG-002)"))

    # LOG-010–012: base required fields present at all.
    for f in BASE_REQUIRED_FIELDS:
        if f not in fm:
            errors.append(ValidationError(index, f"missing required field '{f}' (LOG-010/012/013)"))

    stage = fm.get("stage")
    if stage is not None and stage not in STAGE_VOCAB:
        errors.append(ValidationError(index, f"unrecognized stage '{stage}' — not in the fixed vocabulary (§3)"))

    # LOG-011: feature required except on the constitution entry.
    if stage != "constitution" and "feature" not in fm:
        errors.append(ValidationError(index, "missing 'feature' (required except on the constitution entry, LOG-011)"))

    ts = fm.get("timestamp")
    if ts is not None:
        try:
            datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except ValueError:
            errors.append(ValidationError(index, f"'timestamp' is not valid ISO 8601: {ts!r}"))

    # LOG-020: model-backed pane fields, required unless this stage is mechanical.
    if stage not in MECHANICAL_STAGES and stage is not None:
        for f in MODEL_BACKED_FIELDS:
            if f not in fm:
                errors.append(ValidationError(index, f"missing model-backed field '{f}' for stage '{stage}' (LOG-020)"))
        tier = fm.get("tier")
        if tier is not None and tier not in VALID_TIERS:
            errors.append(ValidationError(index, f"invalid tier '{tier}', expected one of {sorted(VALID_TIERS)}"))
        usage = fm.get("usage")
        if isinstance(usage, dict):
            for uf in ("input_tokens", "output_tokens", "estimated_cost_usd"):
                if uf not in usage:
                    errors.append(ValidationError(index, f"missing usage field '{uf}' (LOG-020)"))

    # LOG-021: decision/feedback presence + valid decision value.
    decision = fm.get("decision")
    if decision not in VALID_DECISIONS:
        errors.append(ValidationError(index, f"invalid decision '{decision}' (LOG-021)"))

    # LOG-022/023/024/025: stage-specific required fields.
    for f in STAGE_SPECIFIC_REQUIRED.get(stage, ()):
        if f not in fm:
            errors.append(ValidationError(index, f"missing '{f}', required on stage '{stage}'"))

    if stage == "triage":
        tr = fm.get("triage_result")
        if tr is not None and tr not in VALID_TRIAGE_RESULTS:
            errors.append(ValidationError(index, f"invalid triage_result '{tr}', expected one of {sorted(VALID_TRIAGE_RESULTS)}"))

    # Carry the prose summary forward on the returned dict — consumers (the
    # dashboard's step-report feed) need it, and LOG-002 already requires
    # every entry to have one. 'summary' is not a defined frontmatter field
    # (see SCHEMA.md §2), so this can't collide with a real field; guard
    # against it anyway in case a future schema version adds one.
    if "summary" not in fm:
        fm["summary"] = prose.strip()

    return fm, errors


def parse_log(text: str) -> ParseResult:
    result = ParseResult()

    header, blocks = _split_entries(text)
    if header is None and text.strip():
        result.errors.append(ValidationError(-1, "missing or malformed schema header line (LOG-001)"))

    if not blocks:
        # Header-only (or empty) file is valid per LOG-AC3.
        return result

    for i, raw in enumerate(blocks):
        entry, errs = _validate_entry(raw, i)
        result.errors.extend(errs)
        if entry is not None:
            result.entries.append(entry)

    return result


def parse_log_file(path: str) -> ParseResult:
    with open(path, encoding="utf-8") as fh:
        return parse_log(fh.read())


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validator.py <path-to-factory-log.md>", file=sys.stderr)
        return 2

    result = parse_log_file(argv[1])
    print(f"Parsed {len(result.entries)} entr{'y' if len(result.entries) == 1 else 'ies'}.")
    for err in result.errors:
        print(str(err), file=sys.stderr)

    if result.errors:
        print(f"{len(result.errors)} validation error(s).", file=sys.stderr)
        return 1

    print("Valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
