# Manual cmux workspace setup (GUI)

A third way to stand up this project's 3 core cmux workspaces (main, design, implementation) — alongside `docs/prompts/setup-cmux-workspaces.md` (paste into a Claude Code session) and `docs/manual-cmux-workspace-setup.md` (run the `cmux` CLI yourself). This version does the workspace creation and naming entirely in the cmux app's UI, with only one unavoidable terminal command at the very end.

## Why one CLI command is still needed

`.specify/cmux-workspaces.json` maps the names `main`/`design`/`implementation` to each workspace's real, opaque ID — the director skill reads this file and addresses workspaces with `--workspace <id>`, since cmux's own naming isn't something its CLI or (as far as this doc's research found) its UI exposes directly. The sidebar shows a workspace's git branch, linked PR, working directory, listening ports, and latest notification — not its ID. So: do all the creating and labeling below in the GUI, then run one `cmux list-workspaces --json` at the end purely to read the IDs off, matched by the labels you just gave them.

## Steps

**1. Confirm you're in "main."** Sit in the workspace you want to become main — this is where the director and dashboard will live. You don't need to do anything to it here; its ID gets read in step 4 along with the other two.

**2. Create the "design" workspace:**
- Press `⌘N` (New Workspace) — opens a new workspace with a terminal surface.
- Press `⌘⇧R` (Rename Workspace) and name it something you'll recognize in step 4, e.g. `design` or `my-project-design` — the sidebar will show this name, and cmux's `list-workspaces --json` output should include it too (or at minimum, its working directory, if you `cd` into your project first).
- `cd` into `my-project` in this workspace's terminal, so it's identifiable by working directory in step 4 even if the display name doesn't come through in the JSON output as expected — this doc's exact JSON field names are unconfirmed (see caveat below).

**3. Create the "implementation" workspace:**
- Same as step 2: `⌘N`, `⌘⇧R` and name it `implementation` (or similar), `cd` into `my-project`.

**4. Look up the three real IDs — the one CLI step:**

```bash
cmux list-workspaces --json | jq
```

Find the three entries matching main / design / implementation (by the names you set in steps 2–3, or by working directory / git branch if names don't appear as expected) and note their ID fields.

**5. Write the mapping** to `.specify/cmux-workspaces.json`:

```json
{
  "main": "<main's id>",
  "design": "<design's id>",
  "implementation": "<implementation's id>"
}
```

**6. Verify** — re-run `cmux list-workspaces --json | jq` and confirm all three IDs in the file exist and are pairwise distinct.

## What NOT to do here

- Don't create review, docs, or PR workspaces in this pass — the pipeline creates those lazily on first use.
- Don't switch focus away from main as your "home base" once this is done — the other two are for the design and implementation panes to use, not for you to live in.
- Don't spawn any panes into design/implementation yet — this is workspace setup only, not feature work.

## Caveat, stated plainly

The `⌘N` / `⌘⇧R` shortcuts and the sidebar's displayed fields (branch, PR, working directory, ports) come from the cmux project's own public documentation, not from running this doc against a live instance as part of this template's own test suite. Specifically unconfirmed:

- Whether a workspace's display name (set via Rename) actually appears in `cmux list-workspaces --json`'s output, or whether that command only ever returns lower-level fields like ID and working directory.
- The exact JSON key names in that output.
- Whether the cmux GUI exposes a workspace's ID anywhere at all (a menu, an info panel, hovering a sidebar entry) that would let you skip step 4 entirely — none was found in the sources checked for this doc.

**When you run this for real, please report back what actually happened** — in particular, whether renamed workspaces show up identifiably in `list-workspaces --json`, and whether the GUI has an ID-display path this doc missed. That will let this doc (and the other two workspace-setup docs, which share the underlying model) be corrected against real behavior.

## Consumers of this file

The director skill reads `.specify/cmux-workspaces.json` at startup and uses those IDs with `--workspace <id>` wherever it currently just says "design workspace" or "implementation workspace."
