#!/usr/bin/env bash
# Thin CLI wrapper — the actual logic lives in scaffold.py (Python is far
# more tractable than bash for the templating/diff work this does).
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec uv run --with pyyaml python3 "$SCRIPT_DIR/scaffold.py" "$@"
