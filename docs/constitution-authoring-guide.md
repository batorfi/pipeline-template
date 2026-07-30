# Constitution authoring guide

This isn't a restatement of what each field in `constitution.template.md` means — the template's own inline comments already do that. This is guidance on picking **real starting values** for a project with no history yet.

## Feature-size triage: the module-boundary definition

> "confined to a single file, or to `<<FILL: a tightly-scoped module boundary>>`"

If you don't have a strong opinion yet, use whatever unit your codebase's own conventions already treat as a cohesive change boundary — a single package, a single service directory, a single React feature folder. Don't overthink this at scaffold time: the triage rubric gets revisited after real features run (see below), so a slightly-wrong first guess is cheap to fix.

## Concurrency caps: both numbers, not just one

- **Per-feature cap**: start at **2–3**. This bounds how many worker panes one feature can have running simultaneously.
- **Project-wide aggregate cap**: start at **roughly double the per-feature cap** (e.g., 4–6) — this is the ceiling across *every* active feature combined, and it's the one that actually protects your account's throughput and the director's own attention when more than one feature is in flight.

If you don't expect to run concurrent features soon, these numbers matter less initially — but fill them in anyway; an unfilled `<<FILL:...>>` blocks scaffolding regardless of how soon you'll need the value.

## Usage budget: "no hard cap" is a legitimate starting answer

A fresh scaffold has zero usage history to size a dollar figure against. It's fine — arguably better — to write `no hard cap, tracked only` for both the per-feature and project-wide budget fields, and add a real number once the dashboard's totals panel shows you what a typical feature actually costs.

## Opus-share ceiling: start at 30%

This is an early-warning signal, not a hard limit — if Opus-tier spend exceeds this percentage of a feature's total cost, the director flags it at the next gate. 30% is a reasonable starting point given the tier table's design (Opus is reserved for architecture critic, code reviewer, and verification diagnosis — a handful of expensive-but-infrequent calls, not the bulk of spend). Watch the dashboard after your first few features and adjust if 30% turns out to trigger constantly or never.

## Sensitive surfaces: add project-specific ones now, not later

Authentication, schema migrations, and public API contracts are pre-filled defaults. Think concretely about what else in *this* codebase deserves the same treatment — billing code, a compliance-regulated module, cryptographic code, anything where a "small"-triaged mistake would be genuinely expensive. Adding these now costs nothing; discovering the gap after a small-triaged feature touches one of them costs a lot more.

## Reviewing and revising — don't skip this after the first few features

The constitution ships with a "Reviewing and revising this constitution" section for a reason. After each feature, check the dashboard's run statistics — escalation rate, review-restart rate, Opus-share trend, whether a "small" triage call turned out wrong — and adjust the values above if the data says so. Log the revision to `factory-log.md`, the same discipline as every other decision this pipeline logs.
