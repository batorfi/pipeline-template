# Workflow overview

The human-facing counterpart to the pipeline concept itself — condensed from `concepts/claude-only-pipeline/20260720-101336_claude-only-spec-driven-multi-agent-development-pipeline-orc.md`. Read that document for full design rationale; this is the operational summary.

## Roles

| Role | Workspace | Default tier |
|---|---|---|
| Director | Main | Opus |
| Researcher | Design | Sonnet |
| Concept writer | Design | Sonnet |
| Architecture designer | Design | Sonnet |
| Architecture critic | Design | **Opus** |
| ADR maker | Design | Sonnet |
| Verifier — diagnosis | Design | **Opus** |
| Verifier — mitigation tasks | dispatched as worker tasks | Sonnet / Haiku |
| Worker — standard-triage task | Implementation | Sonnet |
| Worker — small-triage task | Implementation | Haiku |
| Feature-size triage | Main (director) | Haiku |
| Code reviewer | Review | **Opus** |
| Techwriter | Docs | Sonnet |
| PR writer | PR | Sonnet |

Bolded roles are the pipeline's actual line of defense — everywhere else, a human gate immediately downstream is the primary check.

## The nine gates

1. **Concept gate** (standard only) — approve / revise / reject
2. **Architecture gate** (standard only) — approve / revise / reject
3. **Spec gate** — approve / revise
4. **Plan gate** — approve / revise
5. **Checkpoint gate** (per user-story phase) — approve / revise
6. **Review gate** — approve / **restart** (no revise; restart goes all the way back to triage)
7. **Verification gate** — approve / **reject** (no revise; mitigation happens automatically, capped at 2 rounds, before this gate ever opens)
8. **Docs gate** — approve / revise / reject
9. **PR gate** — approve / revise / reject

A **small**-triaged feature skips gates 1–2 entirely, going straight from a director-drafted inline spec to the spec gate.

## Escalation cascade

A task that fails its scoped tests escalates exactly one tier (Haiku → Sonnet → Opus), carrying the failed diff and error forward. One attempt per tier — a task that still fails at Opus surfaces at the next checkpoint gate for you, not another automated retry.

## Cost control

Two levers, both in `constitution.md`: the feature-size triage (small features skip the pre-spec ceremony entirely) and per-tier budget tracking with an Opus-share ceiling as an early-warning signal. See `docs/constitution-authoring-guide.md` for setting real starting values.

## What this design does not resolve

Two limitations persist regardless of tuning: a spec that under-specifies an edge case won't be caught by any downstream gate (they're all validating against the same incomplete spec), and a feature that looks small at triage but turns out to need real architectural judgment only surfaces that after skipping the gates that would have caught it. See the published concept's critique for the full analysis.
