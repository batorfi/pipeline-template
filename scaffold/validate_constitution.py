"""Structural-completeness validator for a rendered constitution.md.

Implements CONST-001, CONST-002, CONST-003, CONST-AC1, CONST-AC2. Used by
scaffold.sh (SCAF-003) to refuse to consider scaffolding complete while any
<<FILL:...>> marker remains, and to catch a missing required section.

Two independent checks:
  1. Every required section (by heading) is present.
  2. No unresolved <<FILL:...>> marker remains.
Both are reported together, not stop-on-first-error, so a human fixing the
constitution sees everything wrong in one pass.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field

FILL_MARKER_RE = re.compile(r"<<FILL:[^>]*>>")

# Required section headings, per constitution.template.md / CONST-001.
REQUIRED_SECTIONS = [
    "Pipeline template version",
    "Feature-size triage rubric",
    "Model-tier assignment",
    "Concurrency caps",
    "Usage budget",
    "Sensitive surfaces",
    "Pre-spec polish-round cap",
    "Reviewing and revising this constitution",
]


@dataclass
class ConstitutionValidationResult:
    missing_sections: list[str] = field(default_factory=list)
    unresolved_fills: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing_sections and not self.unresolved_fills

    def report(self) -> str:
        lines = []
        if self.missing_sections:
            lines.append("Missing required section(s):")
            lines.extend(f"  - {s}" for s in self.missing_sections)
        if self.unresolved_fills:
            lines.append(f"Unresolved <<FILL:...>> marker(s): {len(self.unresolved_fills)}")
            lines.extend(f"  - {m}" for m in self.unresolved_fills)
        if not lines:
            lines.append("Structurally complete: all required sections present, no unresolved markers.")
        return "\n".join(lines)


def validate_constitution(text: str) -> ConstitutionValidationResult:
    result = ConstitutionValidationResult()

    for section in REQUIRED_SECTIONS:
        # Match as a markdown heading (## Section) — CONST-001 requires the
        # section itself, not just the phrase appearing somewhere in prose.
        heading_re = re.compile(rf"^#{{1,3}}\s+{re.escape(section)}\s*$", re.MULTILINE)
        if not heading_re.search(text):
            result.missing_sections.append(section)

    result.unresolved_fills = FILL_MARKER_RE.findall(text)

    return result


def validate_constitution_file(path: str) -> ConstitutionValidationResult:
    with open(path, encoding="utf-8") as fh:
        return validate_constitution(fh.read())


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_constitution.py <path-to-constitution.md>", file=sys.stderr)
        return 2

    result = validate_constitution_file(argv[1])
    print(result.report())
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
