"""Renders constitution.template.md and the factory-log templates for a
target project. Substitutes only the values scaffold.sh itself knows
(template version, Spec Kit version, scaffold date) — every other
<<FILL:...>> marker is left in place for the human to fill in (CONST-002).
"""

from __future__ import annotations

import re
from datetime import datetime, timezone


def render_constitution(template_text: str, template_version: str, spec_kit_version: str | None) -> str:
    """Substitute only the version-pin block's three known values. Every
    other <<FILL:...>> marker is left untouched, per CONST-002."""
    scaffold_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    values = {
        "template version, e.g. v0.1.0": template_version,
        "as recorded by `specify init`": spec_kit_version or "<<FILL: as recorded by `specify init`>>",
        "date of this scaffold, or the most recent deliberate --sync": scaffold_date,
    }

    def repl(m: re.Match) -> str:
        inner = m.group(1).strip()
        if inner in values:
            return values[inner]
        return m.group(0)  # leave every other marker untouched

    return re.sub(r"<<FILL:\s*(.*?)>>", repl, template_text, flags=re.DOTALL)


def render_entry_zero(template_text: str, template_version: str, spec_kit_version: str | None) -> str:
    scaffold_timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    values = {
        "ISO 8601 UTC timestamp of constitution acceptance, e.g. 2026-07-20T09:00:00Z": scaffold_timestamp,
        "template version, e.g. v0.1.0": template_version,
        "as recorded by `specify init`": spec_kit_version or "<<FILL: as recorded by `specify init`>>",
    }

    def repl(m: re.Match) -> str:
        inner = m.group(1).strip()
        if inner in values:
            return values[inner]
        return m.group(0)

    return re.sub(r"<<FILL:\s*(.*?)>>", repl, template_text, flags=re.DOTALL)
