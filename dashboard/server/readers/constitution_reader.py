"""GET /config's data layer — implements BE-030.

Parses a filled-in constitution.md (per constitution.template.md's structure)
into the tier table, concurrency caps (per-feature and aggregate, CONST-020/021),
and budget figures the frontend needs as denominators for "% of cap used" figures.

Regex-based against the template's known prose shape, not a general markdown
parser — if constitution.template.md's wording changes, this must change with
it in the same release, per the template repository's bundled-versioning rule.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

TIER_TABLE_ROW_RE = re.compile(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", re.MULTILINE)


def _parse_tier_table(text: str) -> dict[str, str]:
    tiers: dict[str, str] = {}
    in_table = False
    for match in TIER_TABLE_ROW_RE.finditer(text):
        role, tier = match.group(1).strip(), match.group(2).strip()
        if role.lower() == "role" or set(role) <= {"-"}:
            in_table = True
            continue
        if in_table and role and tier and not set(tier) <= {"-"}:
            tiers[role] = tier.replace("**", "")
    return tiers


def read_constitution(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"tiers": {}, "caps": {}, "budget": {}, "error": "constitution.md not found"}

    text = path.read_text(encoding="utf-8")

    tiers = _parse_tier_table(text)

    # Whitespace-tolerant search within each section, since the source prose
    # wraps at arbitrary column widths rather than fixed newline positions.
    caps_section_match = re.search(r"## Concurrency caps(.*?)## Usage budget", text, re.DOTALL)
    caps_text = caps_section_match.group(1) if caps_section_match else ""
    per_feature_match = re.search(r"\*\*Per-feature\.\*\*\s*No more than\s+(\S+)", caps_text)
    aggregate_match = re.search(r"\*\*Project-wide aggregate\.\*\*\s*No more than\s+(\S+)", caps_text)

    budget_section_match = re.search(r"## Usage budget(.*?)## Sensitive surfaces", text, re.DOTALL)
    budget_text = budget_section_match.group(1) if budget_section_match else ""
    opus_share_match = re.search(r"exceeds\s+(\S+)\s+of", budget_text)

    return {
        "tiers": tiers,
        "caps": {
            "per_feature_workers": per_feature_match.group(1) if per_feature_match else None,
            "aggregate_workers": aggregate_match.group(1) if aggregate_match else None,
        },
        "budget": {
            "opus_share_ceiling": opus_share_match.group(1) if opus_share_match else None,
        },
    }
