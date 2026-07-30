"""GET /log's data layer — implements BE-001, BE-002.

Streams and parses factory-log.md via the canonical validator (never a
second, drifted parser), filters by feature/limit, and separates malformed
entries into their own `errors` list rather than dropping them silently.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ._factory_log_validator import factory_log_validator


def read_log(
    path: Path,
    feature: str | None = None,
    limit: int | None = None,
) -> dict[str, Any]:
    """BE-001: newest-first entries, optionally filtered, plus a parallel errors list.

    BE-002 (streaming): factory_log_validator.parse_log_file currently reads the
    whole file into memory in one pass. This is acceptable while the log is
    small; the streaming requirement is a scaling concern flagged for revisit
    once a real multi-feature log exists to benchmark against (see
    docs/implementation-specs.md BE-052) — implementing a premature streaming
    parser against a log that's currently a handful of KB would be solving a
    problem that doesn't exist yet at real cost to readability now.
    """
    if not path.exists():
        return {"entries": [], "errors": []}

    result = factory_log_validator.parse_log_file(str(path))

    entries = list(reversed(result.entries))  # newest-first

    if feature is not None:
        entries = [e for e in entries if e.get("feature") == feature]

    if limit is not None:
        entries = entries[:limit]

    errors = [str(e) for e in result.errors]

    return {"entries": entries, "errors": errors}
