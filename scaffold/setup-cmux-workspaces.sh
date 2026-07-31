#!/usr/bin/env bash
# Stands up this project's 3 core cmux workspaces (main, design,
# implementation) and writes .specify/cmux-workspaces.json — the name->ID
# mapping the director skill reads at startup, since cmux addresses
# workspaces only by opaque ID (workspace:<n>), never by name.
#
# Run this FROM INSIDE your scaffolded project's root, in the cmux workspace
# you want to become "main" (the one the director and dashboard will live
# in) — copy-paste directly into your terminal, or:
#
#   docs/setup-cmux-workspaces.sh
#
# (Copied here as docs/setup-cmux-workspaces.sh at scaffold time — this
# source copy lives in the template repo's own scaffold/, not in your
# project.)
#
# This is the same sequence documented in docs/manual-cmux-workspace-setup.md
# as copy-pasteable commands — this script exists so you don't have to
# copy-paste them piecemeal. Confirmed against a real cmux instance
# (2026-07-31): see that doc for the caveats and confirmed-behavior notes
# behind each command choice below (--title is required on every rename,
# --workspace is required even when renaming the workspace you're in, both
# `create` and `rename` print the affected workspace's ID directly).
#
# Requires: cmux CLI on PATH, jq on PATH.
set -euo pipefail

if ! command -v cmux >/dev/null 2>&1; then
  echo "ERROR: cmux is required but not found on PATH." >&2
  echo "Install it: https://cmux.com" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq is required but not found on PATH." >&2
  exit 1
fi

MAPPING_FILE=".specify/cmux-workspaces.json"

if [[ -f "$MAPPING_FILE" ]] && [[ "${1:-}" != "--force" ]]; then
  echo "ERROR: $MAPPING_FILE already exists — this project looks already set up." >&2
  echo "Re-running would create 2 more orphaned workspaces without reusing the" >&2
  echo "existing ones. Pass --force if you really want to create a fresh set" >&2
  echo "(the old design/implementation workspaces are left open, not closed —" >&2
  echo "close them yourself in cmux if you don't want them lingering)." >&2
  exit 1
fi

PROJECT=$(basename "$PWD")

echo "Standing up cmux workspaces for '$PROJECT'..."

MAIN_ID=$(cmux current-workspace --json | jq -r '.workspace_ref')
cmux workspace rename --workspace "$MAIN_ID" --title "${PROJECT}-main" >/dev/null
echo "  main:           $MAIN_ID  (${PROJECT}-main)"

DESIGN_ID=$(cmux workspace create | grep -oE 'workspace:[0-9]+')
cmux workspace rename --workspace "$DESIGN_ID" --title "${PROJECT}-design" >/dev/null
echo "  design:         $DESIGN_ID  (${PROJECT}-design)"

IMPL_ID=$(cmux workspace create | grep -oE 'workspace:[0-9]+')
cmux workspace rename --workspace "$IMPL_ID" --title "${PROJECT}-implementation" >/dev/null
echo "  implementation: $IMPL_ID  (${PROJECT}-implementation)"

mkdir -p "$(dirname "$MAPPING_FILE")"
cat > "$MAPPING_FILE" <<EOF
{
  "main": "$MAIN_ID",
  "design": "$DESIGN_ID",
  "implementation": "$IMPL_ID"
}
EOF

echo ""
echo "Wrote $MAPPING_FILE:"
cat "$MAPPING_FILE"
echo ""
echo "Verify against the live workspace list:"
cmux workspace list --json | jq '.workspaces[] | {ref, title}'

echo ""
echo "Done. You did NOT create review/docs/PR workspaces — the pipeline"
echo "creates those lazily on first use. You're still in main; nothing was"
echo "switched or spawned into design/implementation."
