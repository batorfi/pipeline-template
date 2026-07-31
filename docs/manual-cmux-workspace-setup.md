# Manual cmux workspace setup

The commands for standing up this project's 3 core cmux workspaces (main, design, implementation), run yourself directly in your terminal. Produces `.specify/cmux-workspaces.json`.

Requires the `cmux` CLI on `PATH` (`cmux --version` to check) and `jq` for parsing its `--json` output.

## Why a name→ID mapping file at all

cmux's CLI addresses workspaces by opaque ID (`workspace:<n>`), not by name. Every role skill in this pipeline talks about "the design workspace" / "the implementation workspace" as if those are names cmux understands — they aren't. `.specify/cmux-workspaces.json` is what makes that vocabulary real: the director skill reads it at startup and uses `--workspace <id>` wherever it would otherwise need a name cmux has no concept of.

## Naming convention

`.specify/cmux-workspaces.json` is what makes these roles addressable to the pipeline's skills — but nothing stops the *cmux sidebar itself* from also showing you, at a glance, which workspace is which, so you're not relying on memory or tab order while you work. Give each workspace a real display name via `cmux rename-workspace`, using your project's own directory name as a prefix so it's unambiguous if you ever have more than one of these pipelines running side by side — e.g. for `my-project`: `my-project-main`, `my-project-design`, `my-project-implementation`. This is optional — the pipeline itself only ever reads IDs from the JSON file below, never a display name — but recommended, since it's the difference between a sidebar full of identical-looking "Untitled" entries and one that reads clearly at a glance.

## Steps

Run these from inside your project root, in the cmux workspace you want to become **main** — this is where the director and dashboard will live.

```bash
PROJECT=$(basename "$PWD")

# 1. Rename the current workspace to "<project>-main" and capture its ID.
#    cmux rename-workspace, with no --workspace flag, targets the workspace
#    you're currently in, and prints its ID directly (`OK workspace:<n>`) —
#    confirmed against a real cmux instance, no separate lookup needed.
MAIN_ID=$(cmux rename-workspace "${PROJECT}-main" | grep -oE 'workspace:[0-9]+')
echo "main: $MAIN_ID"

# 2. Create and rename "design". cmux new-workspace also prints the new
#    workspace's ID directly in its own output (`OK workspace:<n>`) —
#    confirmed; no before/after diff against `list-workspaces` is needed.
DESIGN_ID=$(cmux new-workspace | grep -oE 'workspace:[0-9]+')
cmux rename-workspace --workspace "$DESIGN_ID" "${PROJECT}-design"
echo "design: $DESIGN_ID"

# 3. Create and rename "implementation", same pattern.
IMPL_ID=$(cmux new-workspace | grep -oE 'workspace:[0-9]+')
cmux rename-workspace --workspace "$IMPL_ID" "${PROJECT}-implementation"
echo "implementation: $IMPL_ID"
```

`--workspace <id>` on step 2/3's rename does **not** switch you into that workspace — you stay in main throughout, per "What NOT to do here" below.

**4. Write the mapping** to `.specify/cmux-workspaces.json`:

```bash
cat > .specify/cmux-workspaces.json <<EOF
{
  "main": "$MAIN_ID",
  "design": "$DESIGN_ID",
  "implementation": "$IMPL_ID"
}
EOF
```

**5. Verify** all three IDs are real and distinct:

```bash
cmux list-workspaces --json | jq '.workspaces[] | {ref, title}'
cat .specify/cmux-workspaces.json
```

Confirm the three IDs in the file actually appear in `list-workspaces`' output (as each entry's `ref` field) and are pairwise different.

## A note on cmux's own output

Recent `cmux` versions print a one-time notice like `cmux: 'rename-workspace' is now an alias for 'cmux workspace rename'. The legacy form keeps working indefinitely` the first time you use a legacy-form command in a session. Harmless — the commands above keep working exactly as shown — but if it's noisy, set `CMUX_QUIET=1` in your shell to silence it, or switch to the newer noun-verb form (`cmux workspace rename`, `cmux workspace create`, `cmux workspace list`) directly; both forms behave identically as far as this doc is concerned.

## What NOT to do here

- Don't create review, docs, or PR workspaces — the pipeline creates those lazily on first use, since they're single-pane and short-lived.
- Don't switch into the new design/implementation workspaces as part of this — stay in main.
- Don't spawn any panes into the new workspaces yet — this is workspace setup only, not feature work.

## Confirmed against a real cmux instance (2026-07-31)

Earlier drafts of this doc carried several unconfirmed assumptions, written from the CLI reference alone. A real run resolved them:

- `cmux new-workspace` and `cmux rename-workspace` **do** print the new/target workspace's ID directly in their own output (`OK workspace:<n>`) — no before/after diff against `list-workspaces` is needed, contrary to what an earlier draft assumed as the fallback path.
- The JSON key for a workspace's ID is `ref` (e.g. `"ref": "workspace:16"`) inside each entry of `list-workspaces --json`'s `workspaces` array; `current-workspace --json` wraps the same value one level up as `workspace_ref`.
- `cmux rename-workspace --workspace <id> <name>` works as documented, targeting a workspace other than the current one without switching into it.

Still unconfirmed: whether a multi-word name needs different quoting than shown above (the real run used single-word, hyphenated names throughout, so this wasn't exercised) — report back if you hit a quoting issue.

## Consumers of this file

The director skill reads `.specify/cmux-workspaces.json` at startup and uses those IDs with `--workspace <id>` wherever it currently just says "design workspace" or "implementation workspace."
