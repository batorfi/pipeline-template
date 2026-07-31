# Manual cmux workspace setup

The commands for standing up this project's 3 core cmux workspaces (main, design, implementation), run yourself directly in your terminal. Produces `.specify/cmux-workspaces.json`.

Requires the `cmux` CLI on `PATH` (`cmux --version` to check) and `jq` for parsing its `--json` output.

## Why a name→ID mapping file at all

cmux's CLI addresses workspaces by opaque ID (`workspace:<n>`), not by name. Every role skill in this pipeline talks about "the design workspace" / "the implementation workspace" as if those are names cmux understands — they aren't. `.specify/cmux-workspaces.json` is what makes that vocabulary real: the director skill reads it at startup and uses `--workspace <id>` wherever it would otherwise need a name cmux has no concept of.

## Naming convention

`.specify/cmux-workspaces.json` is what makes these roles addressable to the pipeline's skills — but nothing stops the *cmux sidebar itself* from also showing you, at a glance, which workspace is which, so you're not relying on memory or tab order while you work. Give each workspace a real display name via `cmux workspace rename`, using your project's own directory name as a prefix so it's unambiguous if you ever have more than one of these pipelines running side by side — e.g. for `my-project`: `my-project-main`, `my-project-design`, `my-project-implementation`. This is optional — the pipeline itself only ever reads IDs from the JSON file below, never a display name — but recommended, since it's the difference between a sidebar full of identical-looking "Untitled" entries and one that reads clearly at a glance.

## Steps

Run these from inside your project root, in the cmux workspace you want to become **main** — this is where the director and dashboard will live.

```bash
PROJECT=$(basename "$PWD")

# 1. Rename the current workspace to "<project>-main" and capture its ID.
#    `cmux workspace rename`, with no --workspace flag, targets the
#    workspace you're currently in, and prints its ID directly
#    (`OK workspace:<n>`) — confirmed against a real cmux instance, no
#    separate lookup needed.
MAIN_ID=$(cmux workspace rename --title "${PROJECT}-main" | grep -oE 'workspace:[0-9]+')
echo "main: $MAIN_ID"

# 2. Create and rename "design". `cmux workspace create` also prints the
#    new workspace's ID directly in its own output (`OK workspace:<n>`) —
#    confirmed; no before/after diff against `workspace list` is needed.
DESIGN_ID=$(cmux workspace create | grep -oE 'workspace:[0-9]+')
cmux workspace rename --workspace "$DESIGN_ID" --title "${PROJECT}-design"
echo "design: $DESIGN_ID"

# 3. Create and rename "implementation", same pattern.
IMPL_ID=$(cmux workspace create | grep -oE 'workspace:[0-9]+')
cmux workspace rename --workspace "$IMPL_ID" --title "${PROJECT}-implementation"
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
cmux workspace list --json | jq '.workspaces[] | {ref, title}'
cat .specify/cmux-workspaces.json
```

Confirm the three IDs in the file actually appear in `workspace list`'s output (as each entry's `ref` field) and are pairwise different.

## A note on cmux's own output

The steps above use `cmux workspace rename` / `cmux workspace create` / `cmux workspace list` — the current noun-verb command form. Earlier drafts of this doc used the older `cmux rename-workspace` / `cmux new-workspace` / `cmux list-workspaces` form; recent `cmux` versions keep those working as aliases indefinitely, but print a one-time per-session notice the first time each is used (`cmux: 'rename-workspace' is now an alias for 'cmux workspace rename'...`), which the commands above avoid entirely. If you still see it (e.g. from a script or habit using the older form), it's harmless — everything keeps working — but you can also set `CMUX_QUIET=1` in your shell to silence it.

## What NOT to do here

- Don't create review, docs, or PR workspaces — the pipeline creates those lazily on first use, since they're single-pane and short-lived.
- Don't switch into the new design/implementation workspaces as part of this — stay in main.
- Don't spawn any panes into the new workspaces yet — this is workspace setup only, not feature work.

## Confirmed against a real cmux instance (2026-07-31)

Earlier drafts of this doc carried several unconfirmed assumptions, written from the CLI reference alone. A real run resolved them:

- `cmux workspace create` and `cmux workspace rename` **do** print the new/target workspace's ID directly in their own output (`OK workspace:<n>`) — no before/after diff against `workspace list` is needed, contrary to what an earlier draft assumed as the fallback path.
- The JSON key for a workspace's ID is `ref` (e.g. `"ref": "workspace:17"`) inside each entry of `workspace list --json`'s `workspaces` array; `current-workspace --json` wraps the same value one level up as `workspace_ref`.
- `cmux workspace rename --workspace <id> --title <name>` works as documented, targeting a workspace other than the current one without switching into it. **Also caught by a real run:** `cmux workspace rename` requires `--title <name>` — a bare positional name (`cmux workspace rename "some-name"`, no `--title`) fails with `Error: workspace rename requires --title <new>`. The steps above already use `--title`; don't drop it if typing this by hand.

Still unconfirmed: whether a multi-word name needs different quoting than shown above (the real run used single-word, hyphenated names throughout, so this wasn't exercised) — report back if you hit a quoting issue.

## Consumers of this file

The director skill reads `.specify/cmux-workspaces.json` at startup and uses those IDs with `--workspace <id>` wherever it currently just says "design workspace" or "implementation workspace."
