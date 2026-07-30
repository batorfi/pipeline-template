# Manual cmux workspace setup

An alternative to `docs/prompts/setup-cmux-workspaces.md` for standing up this project's 3 core cmux workspaces (main, design, implementation) — this version is commands you run yourself, directly in your terminal, instead of a prompt you paste into a Claude Code session. Use whichever fits how you work; both produce the same result: `.specify/cmux-workspaces.json`.

Requires the `cmux` CLI on `PATH` (`cmux --version` to check) and `jq` for parsing its `--json` output.

## Why a name→ID mapping file at all

cmux's CLI has no workspace-naming flag — `cmux new-workspace` takes no name argument, and workspaces are addressed only by opaque ID. Every role skill in this pipeline talks about "the design workspace" / "the implementation workspace" as if those are names cmux understands — they aren't. `.specify/cmux-workspaces.json` is what makes that vocabulary real: the director skill reads it at startup and uses `--workspace <id>` wherever it would otherwise need a name cmux has no concept of.

## Steps

Run these from inside your project root, in the cmux workspace you want to become **main** — this is where the director and dashboard will live.

**1. Record the current workspace's ID as "main":**

```bash
cmux current-workspace --json | jq
```

Note the ID field in the output (confirm its exact key against your `cmux` version — this doc hasn't been run against a live instance yet, see the caveat below).

**2. Create the "design" and "implementation" workspaces:**

```bash
cmux list-workspaces --json > /tmp/cmux-before.json
cmux new-workspace
cmux list-workspaces --json > /tmp/cmux-after.json
diff <(jq -S . /tmp/cmux-before.json) <(jq -S . /tmp/cmux-after.json)
```

The diff shows the newly created workspace — record its ID as "design." Repeat the same three commands (before/new/after/diff) once more for "implementation." If `cmux new-workspace` turns out to print the new ID directly in its own output on your version, skip the before/after diff and just use that instead — check your terminal's output before resorting to the diff.

**3. Write the mapping** to `.specify/cmux-workspaces.json`, exactly this shape:

```bash
cat > .specify/cmux-workspaces.json <<EOF
{
  "main": "<id from step 1>",
  "design": "<first id from step 2>",
  "implementation": "<second id from step 2>"
}
EOF
```

**4. Verify** all three IDs are real and distinct:

```bash
cmux list-workspaces --json | jq
cat .specify/cmux-workspaces.json
```

Confirm the three IDs in the file actually appear in `list-workspaces`' output and are pairwise different.

## What NOT to do here

- Don't create review, docs, or PR workspaces — the pipeline creates those lazily on first use, since they're single-pane and short-lived.
- Don't switch into the new design/implementation workspaces as part of this — stay in main.
- Don't spawn any panes into the new workspaces yet — this is workspace setup only, not feature work.

## Caveat, stated plainly

Written from the `cmux` CLI reference alone — **not yet run against a live cmux instance** as part of this template's own test suite. Specifically unconfirmed:

- Whether `cmux new-workspace` prints the new workspace's ID directly (in which case the before/after diff in step 2 is unnecessary), or whether a diff against `list-workspaces` is genuinely required.
- The exact JSON key name for a workspace's ID in `current-workspace --json` / `list-workspaces --json` output.

**When you run this for real, please report back what actually happened** — this doc (and `docs/prompts/setup-cmux-workspaces.md`, which shares the same underlying steps) can then be corrected against real behavior.

## Consumers of this file

The director skill reads `.specify/cmux-workspaces.json` at startup and uses those IDs with `--workspace <id>` wherever it currently just says "design workspace" or "implementation workspace."
