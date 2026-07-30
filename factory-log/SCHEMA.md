# factory-log.md Schema — v1

Canonical schema for `.specify/factory-log.md`, the single, append-only, project-wide record every pane in the pipeline logs to. This is the source of truth `docs/implementation-specs.md` §2 (LOG-001–LOG-024) derives from and that the dashboard backend's parser (`GET /log`, `GET /stats`) validates against — implements LOG-001 through LOG-024 in full.

Any tool that reads or writes this file — a pane's own logging step, the dashboard backend, `scaffold.sh`'s validators — must conform to this document. If this schema version changes, every consumer changes with it in the same release (see the template repository's bundled-versioning discipline).

## 1. File-level format

**LOG-001 — Header line.** The file MUST begin with exactly one header line, before any entry:

```
<!-- factory-log schema v1 — see factory-log/SCHEMA.md -->
```

The version number in the header (`v1` here) is the schema version this file was created under. A file with no header, or a header naming a version this parser doesn't recognize, MUST be treated as a validation error — never silently assumed to be the current version.

**LOG-002 — Entry format.** Every entry after the header MUST be:
1. A YAML frontmatter block, delimited by `---` on its own line at the start and end.
2. Immediately followed by a plain-language prose summary (one or more paragraphs of markdown, no further structure required).

Entries are appended in chronological order. There is no entry separator required beyond the frontmatter's own `---` delimiters and normal markdown paragraph spacing.

**LOG-003 — Append-only.** The file MUST NEVER be edited, reordered, or truncated after an entry is written — only appended to. Any writer MUST open the file in append mode. A tool that reads the whole file, modifies it, and writes it back is non-conformant, even if the resulting content looks correct — the guarantee this schema exists to provide is that the file's history is tamper-evident by construction (append-only), not just typically-correct in practice.

## 2. Entry frontmatter fields

### 2.1 Required on every entry (LOG-010–LOG-013)

| Field | Type | Rule ID | Description |
|---|---|---|---|
| `timestamp` | string, ISO 8601, UTC | LOG-010 | When this entry's work completed (or, for a gate-presentation entry, when it was presented). |
| `feature` | string | LOG-011 | The feature identifier this entry belongs to. Absent ONLY on the single `constitution` entry that precedes any feature (entry zero). |
| `stage` | string, one of §3's fixed vocabulary | LOG-012 | What kind of entry this is. Any value outside the fixed vocabulary is a validation error (see §3). |
| `duration_seconds` | integer, ≥ 0 | LOG-013 | Wall-clock time this entry's work took. |

### 2.2 Conditional fields, required per entry type (LOG-020–LOG-024)

**LOG-020 — Model-backed pane fields.** REQUIRED whenever the entry was produced by a model-backed pane (i.e., every stage except purely mechanical director actions like `feature_init`):

| Field | Type | Description |
|---|---|---|
| `pane` | string | Which role produced this entry (e.g., `researcher`, `worker`, `code-reviewer`). |
| `tier` | string, one of `opus`, `sonnet`, `haiku` | The model tier that ran. |
| `attempt` | integer, ≥ 1 | Attempt number within this stage — increments on escalation or retry. |
| `escalated_from` | string or `null` | The prior tier, if this entry is an escalation retry; `null` on a first attempt. |
| `usage.input_tokens` | integer | |
| `usage.output_tokens` | integer | |
| `usage.estimated_cost_usd` | number | Labeled as an estimate unless reconciled against an authoritative billed figure (see the template-repo concept's totals-panel spec). |

**LOG-021 — Gate fields.** REQUIRED once a gate has been answered by a human; `null` while only recording what's ready for the gate, before the human responds:

| Field | Type | Description |
|---|---|---|
| `decision` | string or `null` | One of `approve`, `revise`, `reject`, `restart`, `mitigate` — the specific set depends on which gate (see the pipeline concept's per-gate move sets). `null` until answered. |
| `feedback` | string or `null` | The human's free-text feedback, if any, on a revise/restart. |

Convention: a gate's presentation and its resolution are two separate log entries (a "presented" entry with `decision: null`, followed later by a "resolved" entry once the human answers), not one entry mutated in place — this is required by LOG-003's append-only rule. The resolution entry references the presentation entry by matching `stage` + `feature` + being the next entry of that `stage`/`feature` pair in the file. Do not mix this convention with a single-entry-updated-via-append approach; pick this one and apply it consistently across every writer.

**LOG-022 — Checkpoint fields.** REQUIRED on `checkpoint_gate` entries:

| Field | Type | Description |
|---|---|---|
| `phase` | string | Which user-story phase this checkpoint covers. |

**LOG-023 — Worker task fields.** REQUIRED on `worker_task` entries:

| Field | Type | Description |
|---|---|---|
| `task_id` | string | The `tasks.md` task ID (e.g., `T014`). |
| `parallel_group` | string or `null` | The `[P]` group this task belongs to, if any. |

**LOG-024 — Verification fields.** REQUIRED on `verification_gate` entries:

| Field | Type | Description |
|---|---|---|
| `story_id` | string | Which user story this verification pass covers. |
| `mitigation_round` | integer, 0–2 | 0 for the initial verification attempt; 1 or 2 for a mitigation round (capped at 2 per the pipeline concept). |

**LOG-025 — Triage field.** REQUIRED on `triage` entries:

| Field | Type | Description |
|---|---|---|
| `triage_result` | string, one of `small`, `standard` | The classification outcome. |

Note: `triage` is the director's own classification, not a human-answered gate — `decision` and `feedback` (LOG-021) do not apply to it and should be `null`/omitted on a `triage` entry. `triage_result` is a dedicated field precisely so the gate-outcome vocabulary in `decision` (`approve`/`revise`/`reject`/`restart`/`mitigate`) never has to be overloaded with a non-gate classification value.

## 2.5 The `summary` field (synthesized, not written in frontmatter)

The reference validator (`validator.py`) adds a `summary` key to each parsed entry's returned dict, populated from the entry's prose body (LOG-002) — this is not a frontmatter field a writer sets directly, it's how the parser carries the required prose forward to consumers (e.g., the dashboard's step-report feed) without them having to re-parse the raw block themselves. Do not write a literal `summary:` field in an entry's frontmatter; if a future schema version needs a real frontmatter field with that name, the validator's synthesis is skipped in favor of the real value (see the guard in `_validate_entry`).

## 3. Fixed stage-identifier vocabulary

`stage` MUST be exactly one of:

```
constitution, feature_init, triage, researcher, concept_gate, architecture_gate,
adr, spec_gate, plan_gate, checkpoint_gate, worker_task, review_gate,
verification_gate, docs_gate, pr_gate
```

No other value is valid. A parser encountering an unrecognized `stage` value MUST treat it as a validation error, not silently ignore or pass through the entry — this is the mechanism that catches schema drift (a writer using an outdated or invented stage name) early, rather than letting malformed data accumulate silently in an append-only file that can never be corrected after the fact.

## 4. Validation behavior

- A single malformed entry (missing a required field, invalid `stage`, malformed YAML) MUST produce a validation error identifying that specific entry, and MUST NOT prevent parsing of the well-formed entries around it (LOG-AC2).
- A file containing only the header line, no entries, is a valid, empty log — not an error (LOG-AC3).
- A file missing the header line entirely, or an entry with frontmatter fields present but no prose summary following it, is malformed at the file-format level (LOG-001/LOG-002) and should be flagged distinctly from a single-entry field-level error.

## 5. Example: one complete entry, standard-triage worker task

```yaml
---
timestamp: 2026-07-20T14:32:07Z
feature: 001-rate-limit-middleware
stage: worker_task
pane: worker
tier: sonnet
attempt: 1
escalated_from: null
task_id: T014
parallel_group: P2
usage:
  input_tokens: 4820
  output_tokens: 1390
  estimated_cost_usd: 0.09
duration_seconds: 118
decision: null
feedback: null
---
Implemented rate-limit middleware in src/api/middleware/ per T014. Added
token-bucket limiter with configurable window, plus unit tests covering
the boundary and burst cases. Scoped tests pass.
```

## 6. Example: entry zero (constitution creation)

```yaml
---
timestamp: 2026-07-20T09:00:00Z
stage: constitution
duration_seconds: 0
decision: approve
feedback: null
---
Constitution authored and accepted: triage rubric, model-tier table,
concurrency caps (per-feature and aggregate), usage budget with Opus-share
ceiling, sensitive-surface list, pre-spec polish-round cap. Pipeline
template v0.1.0, Spec Kit version confirmed at scaffold time.
```

Note: `feature` is absent here per LOG-011 — this entry precedes any feature.

## 7. Non-goals of this schema version

- No support for editing or retracting a prior entry — corrections are new entries, not mutations (LOG-003).
- No cross-file references beyond the `feature` tag and the presentation/resolution pairing convention in LOG-021 — this schema does not define a general foreign-key mechanism.
- No built-in support for log rollover/archival file-splitting — if the file's unbounded growth becomes a practical problem (per the pipeline concept's acknowledgment), that's a consumer-side (backend) streaming/archival concern, not a schema-level one; this schema only defines what one file's contents look like.
