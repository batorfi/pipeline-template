#!/usr/bin/env bash
# Thin CLI wrapper — the actual logic lives in scaffold.py (Python is far
# more tractable than bash for the templating/diff work this does).
#
# Requires `uv` (https://docs.astral.sh/uv/) — a stated prerequisite, not
# silently degraded around, so a missing `uv` fails fast with a clear,
# actionable message instead of a confusing downstream error.
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv is required but not found on PATH." >&2
  echo "Install it: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec uv run --with pyyaml python3 "$SCRIPT_DIR/scaffold.py" "$@"
