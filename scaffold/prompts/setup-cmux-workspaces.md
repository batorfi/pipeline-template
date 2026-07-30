# Prompt: stand up the 3 core cmux workspaces

Paste this into a Claude Code session running inside cmux, in the workspace you want to become **main** (i.e., the one you're already sitting in — this is where the director and dashboard will live). This implements scaffold step 2 / T068.

**Why this exists, not just "run three commands":** cmux's CLI has no workspace-naming flag (`cmux new-workspace` takes no name argument — see `docs/cmux/cli-reference.md`). Workspaces are addressed only by opaque ID. Every role skill in this pipeline talks about "the design workspace" / "the implementation workspace" as if those are names cmux understands — they aren't. This prompt creates the workspaces *and* writes a name→ID mapping file so the director skill has something real to read instead of a name cmux has no concept of.

---

## The prompt

```
Stand up the cmux workspaces this project's pipeline needs, per
docs/scaffolding-guide.md step 2 and the director skill's workspace model.

1. Confirm the workspace you're currently in — this becomes "main." Run:
   cmux current-workspace --json
   Record its ID.

2. Create two new workspaces:
   cmux new-workspace
   cmux new-workspace
   After each, run `cmux list-workspaces --json` and diff against the
   previous listing to identify which ID was just created (new-workspace
   itself doesn't return the ID directly in the reference I have — confirm
   this against your actual cmux version's output; if it does return an ID
   directly, use that instead of diffing).

3. Assign the two new IDs as "design" and "implementation," in the order
   created. Note: review, docs, and PR workspaces are NOT created here —
   the base concept creates those lazily on first use, since they're
   single-pane and short-lived.

4. Write the mapping to .specify/cmux-workspaces.json in this project,
   exactly this shape:
   {
     "main": "<id from step 1>",
     "design": "<first id from step 2>",
     "implementation": "<second id from step 2>"
   }

5. Verify: run `cmux list-workspaces --json` one more time and confirm all
   three IDs in the file actually exist and are distinct from each other.

6. Print the final mapping so I can see it, and confirm you did NOT create
   review/docs/PR workspaces (those come later, on demand).

Do not select/switch into the new workspaces as part of this — stay in main.
Do not spawn any panes into them yet — this is workspace setup only, not
feature work.
```

---

## What this produces

`.specify/cmux-workspaces.json`, e.g.:

```json
{
  "main": "ws_a1b2c3",
  "design": "ws_d4e5f6",
  "implementation": "ws_g7h8i9"
}
```

## Caveat, stated plainly

This prompt was written from `docs/cmux/cli-reference.md` alone — it has **not been run against a live cmux instance** as part of this template's own test suite (no live cmux was available when this repository was built; see `dashboard/server/NOTES.md` for the same caveat affecting `/panes`). Specifically unconfirmed:

- Whether `cmux new-workspace`'s own output includes the new workspace's ID directly (in which case step 2's diff-and-compare is unnecessary and should be simplified), or whether a diff against `list-workspaces` is genuinely required.
- The exact field name for a workspace's ID in `list-workspaces --json`'s output (assumed to exist; exact key name not confirmed).

**When you run this for real, please report back what actually happened** — specifically whether `new-workspace` returns an ID directly — so this prompt (and the director skill's consumption of `cmux-workspaces.json`) can be corrected against real behavior rather than the reference doc's necessarily incomplete description.

## Consumers of this file

The director skill should read `.specify/cmux-workspaces.json` at startup (alongside its existing startup checklist) and use those IDs with `--workspace <id>` wherever it currently just says "design workspace" or "implementation workspace" — see the director skill's own TODO note pointing back here.
