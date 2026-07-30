# Project Constitution

Rendered from pipeline-template's `constitution.template.md`, fully filled in for this project. Everything below not overridden with a stated reason is a pipeline-wide default.

## Pipeline template version

This project was scaffolded from pipeline-template v0.1.0.
Spec Kit version: 2026.7.1.
Last synced: 2026-07-20.
factory-log schema version: v1 (see `factory-log/SCHEMA.md`).

## Feature-size triage rubric

A feature is **small** if all of the following hold:
- Confined to a single file, or to a single package under src/.
- Introduces no new user story.
- Touches none of the sensitive surfaces named below.

A feature is **standard** otherwise. When in doubt, triage as standard — the cost of an
unnecessary pre-spec pipeline is lower than the cost of skipping architectural judgment
a feature actually needed.

Log every triage decision to `factory-log.md` (stage `triage`, field `triage_result`),
with the reasoning in the entry's prose — this is what lets the rubric above be
tightened later using real data instead of guesswork.

## Model-tier assignment

Default tiers, per the published pipeline concept — override only with a stated reason
if this project's risk profile genuinely differs from the pipeline default:

| Role | Default tier |
|---|---|
| Director | Opus |
| Researcher | Sonnet |
| Concept writer | Sonnet |
| Architecture designer | Sonnet |
| Architecture critic | Opus |
| ADR maker | Sonnet |
| Verifier — diagnosis | Opus |
| Verifier — mitigation tasks | Sonnet / Haiku, by task triage |
| Worker — standard-triage task | Sonnet |
| Worker — small-triage task | Haiku |
| Feature-size triage classification | Haiku |
| Code reviewer | Opus |
| Techwriter | Sonnet |
| PR writer | Sonnet |

**Escalation cascade.** A task that fails its scoped tests escalates exactly one tier
(Haiku → Sonnet → Opus), carrying the failed diff and error forward as context. One
attempt per tier — a task that still fails at Opus is not retried again automatically;
it surfaces at the next checkpoint gate for human attention. Log every attempt and
escalation to `factory-log.md` (fields `tier`, `attempt`, `escalated_from`).

## Concurrency caps

**Per-feature.** No more than 3 concurrent worker panes per
feature. Start conservative and revise using real usage data — see "Reviewing and
revising this constitution," below.

**Project-wide aggregate.** No more than 6 concurrent worker
panes across *all* active features combined, regardless of how many features are
individually within their own per-feature cap. This exists because the actual ceiling
that matters — total load on the account and on the single director's own attention —
is project-wide, not per-feature; a project running three features each within a
per-feature cap of 3 could otherwise spawn 9 workers at once with nothing preventing it.

## Usage budget

**Per-feature.** Total budget per feature: no hard cap, tracked only.

**Project-wide aggregate.** Total budget across all active features: no hard cap, tracked only. Distinct from the per-feature figure for the same
reason the concurrency cap has both levels — the account's actual spend ceiling is
project-wide.

Both budgets are tracked per tier, not as a single aggregate figure — Opus and Haiku
spend behave differently at the same dollar total, and a combined figure can hide a
problem.

**Opus-share ceiling.** If Opus-tier spend exceeds 30% of
a feature's total cost, this is an early-warning signal — flag it at the next gate
presentation rather than waiting for the feature to complete.


## Pre-spec polish-round cap

Architecture designer and critic loop for at most 3 rounds
before the director presents the architecture gate regardless of whether they've fully
converged. This is a polish budget, not an approval mechanism — the gate itself is
still where the real decision happens.

## Reviewing and revising this constitution

This constitution is not fixed at scaffold time. After each feature, review the
dashboard's run statistics — escalation rate, review-restart rate, Opus-share trend,
whether any "small" triage call turned out wrong — and revise the values above if the
data warrants it. Log any revision to `factory-log.md` as its own entry, the same
discipline applied to every other decision this pipeline makes.
