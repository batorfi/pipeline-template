#!/usr/bin/env bash
# Bootstrap installer — makes scaffold.sh runnable directly from the web
# without cloning the repo yourself first:
#
#   curl -fsSL https://raw.githubusercontent.com/batorfi/pipeline-template/main/install.sh \
#     | bash -s -- --template-version v0.1.4 --target ./my-project
#
# All arguments after `--` are passed straight through to scaffold/scaffold.sh
# (including --sync). This script's only job is: get a copy of the template
# repo onto disk (git or curl+tar, whichever's available), then exec the real
# scaffold script from inside it — it does not duplicate any scaffolding
# logic itself.
#
# Requires `uv` (https://docs.astral.sh/uv/) — a stated prerequisite, checked
# up front rather than discovered as a confusing failure partway through.
set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "ERROR: uv is required but not found on PATH." >&2
  echo "Install it: https://docs.astral.sh/uv/getting-started/installation/" >&2
  exit 1
fi

TEMPLATE_REPO="batorfi/pipeline-template"
TEMPLATE_REPO_URL="https://github.com/${TEMPLATE_REPO}.git"

# Find the pinned tag from the passed-through arguments, since we need it to
# fetch the right ref — a plain default-branch clone would defeat the whole
# point of pinned, bundled versioning this template repo is built around.
TEMPLATE_VERSION=""
args=("$@")
for ((i = 0; i < ${#args[@]}; i++)); do
  if [[ "${args[$i]}" == "--template-version" ]] && [[ $((i + 1)) -lt ${#args[@]} ]]; then
    TEMPLATE_VERSION="${args[$((i + 1))]}"
    break
  fi
done

if [[ -z "$TEMPLATE_VERSION" ]]; then
  echo "ERROR: --template-version <tag> is required (e.g. --template-version v0.1.2)." >&2
  echo "See: https://github.com/${TEMPLATE_REPO}/tags" >&2
  exit 1
fi

WORKDIR="$(mktemp -d)"
cleanup() { rm -rf "$WORKDIR"; }
trap cleanup EXIT

if command -v git >/dev/null 2>&1; then
  git clone --branch "$TEMPLATE_VERSION" --depth 1 "$TEMPLATE_REPO_URL" "$WORKDIR/repo" >&2
elif command -v curl >/dev/null 2>&1; then
  # No git available: fall back to downloading the tagged tarball directly
  # from GitHub's archive endpoint — still works against a public repo with
  # nothing but curl and tar.
  echo "git not found — falling back to tarball download" >&2
  curl -fsSL "https://github.com/${TEMPLATE_REPO}/archive/refs/tags/${TEMPLATE_VERSION}.tar.gz" \
    | tar -xz -C "$WORKDIR"
  mv "$WORKDIR"/pipeline-template-*/ "$WORKDIR/repo"
else
  echo "ERROR: neither git nor curl found. Install one and retry." >&2
  exit 1
fi

# Note: scaffold.sh's own logic (scaffold.py) clones the template repo again
# into its own temp directory to actually copy artifacts from — this script's
# clone exists only to get scaffold.sh itself onto disk in the first place.
# Two clones of a small, shallow (--depth 1) repo is a fine trade for keeping
# this bootstrap script dumb and not duplicating any scaffolding logic.
exec "$WORKDIR/repo/scaffold/scaffold.sh" "$@"
