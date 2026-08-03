# Working with docs-synthesizer

The mechanics of using the `docs-synthesizer` skill — a role invoked directly by you, any time, for broad documentation that draws on the whole project's history rather than one feature's diff. See `skills/docs-synthesizer/SKILL.md` for what it actually produces; this doc covers how to ask for it.

## How it's different from techwriter

`techwriter` only exists inside one feature's pipeline — the director spawns it after the verification gate approves, and it works from that one feature's spec/plan/ADRs/diff. `docs-synthesizer` is never spawned by the director. You invoke it yourself, in your main workspace, whenever you want — after one feature, after several, or long after any pipeline activity at all. It reads across every feature's history, not one diff.

If what you actually want is "update the docs to reflect this one change that just shipped," that's techwriter's job, done automatically as part of that feature's own pipeline — you don't need to ask for it separately.

## How to invoke it

Say what you want directly, naming one of the eight output types and roughly what it should cover:

- *"Use docs-synthesizer to write a technical overview of the project."*
- *"Use docs-synthesizer to write a how-to guide for setting up the dev environment."*
- *"Use docs-synthesizer to write a whitepaper about why this project uses a progressive rendering pipeline."*
- *"Use docs-synthesizer to write a concept note about the resize invariant."* (single-note mode)
- *"Use docs-synthesizer to survey feature 002's ADRs for concept notes worth writing."* (survey mode — proposes candidates, doesn't write them yet)
- *"Use docs-synthesizer to build the ADR index."*
- *"Use docs-synthesizer to update the FAQ with anything new from feature 003's clarify stage."*
- *"Use docs-synthesizer to add a glossary entry for 'checkpoint gate'."*
- *"Use docs-synthesizer to write the onboarding runbook."*

Be specific about scope where it matters — "the whole project" versus "just feature 002" changes what it reads before writing.

## What it reads before writing

Every feature's `specs/*/` (spec, plan, ADRs), `.specify/factory-log.md` (or `.specify/factory-log/*.md` if your project uses the sharded form), the current codebase, and whatever's already in `docs/` — so it builds on existing conventions rather than duplicating or contradicting them.

## The eight output types, at a glance

| Type | What it's for | Where it lives |
|---|---|---|
| Technical overview | Orient a new technical reader to the whole system | wherever your project's docs conventions put this — `docs/introduction.md` or similar |
| How-to guide | Get a reader from "I want to do X" to "I did X" | `docs/` |
| Whitepaper | The project's *why* — motivation and design philosophy, for an external/evaluative reader | `docs/` |
| Atomic concept note | One idea, densely linked to related ideas | `docs/concepts/<timestamp>-<slug>.md` |
| ADR index / MOC | One page indexing every ADR, browsable | `docs/concepts/_index.md` |
| FAQ | Recurring points of confusion, sourced from real clarify-stage Q&A | `docs/faq.md` |
| Glossary | Project-specific term definitions | `docs/glossary.md` |
| Onboarding runbook | Zero to first contribution, checklist-first | `docs/onboarding.md` |

## Review

Not a numbered pipeline gate — this role sits outside any single feature's lifecycle — but still human-reviewed before being final. It presents a draft; you approve or send back specific feedback, same as any other role's output.

## Caveat, stated plainly

This role and its eight modes have not yet been run against a real project's full history end-to-end. The design is grounded in what's actually available (real ADRs, real `factory-log.md` entries, real clarify-stage Q&A) and follows the same non-fabrication discipline as `techwriter`, but the first real use of each output type should be treated as the thing that actually validates whether the mode's expectations hold up — report back what you find.
