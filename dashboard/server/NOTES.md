# Dashboard backend — Phase 1 notes

Real, working FastAPI app: 5 endpoints (`/log`, `/tasks`, `/panes`, `/config`, `/stats`), 11 passing pytest tests. Verified end-to-end via `TestClient` against real fixture data, not just unit-tested in isolation.

## Bugs found and fixed while building this (not just checked off)

1. **`compute_stats` order-dependence.** Initially computed escalation/restart stats by iterating entries in whatever order the caller passed them — but `/log` returns newest-first for display, and the stats logic needs to see a `triage` entry before the `worker_task` entries it classifies. Fixed by sorting internally by timestamp regardless of input order; added `test_order_independence` specifically to prevent this regression.
2. **Constitution-parsing regex mismatch.** First pass at `constitution_reader.py`'s cap-extraction regexes didn't match the actual `**Per-feature.**` / `**Project-wide aggregate.**` bold-label format used in `constitution.template.md` — caught immediately by testing against the real fixture rather than assuming the regex was right.

## Known caveats, carried forward from the specs (not resolved here)

- **`/panes`' exact response shape is unconfirmed.** `panes_reader.py` implements the documented commands (`ping`, `list-panels --json`, `list-pane-surfaces --json`) and parses defensively (multiple possible key names, `panes_unavailable` on any failure), but the actual field names in cmux's JSON output haven't been verified against a live instance. When one is available, confirm `panels_data`'s actual shape and adjust the key lookups in `read_panes`.
- **No convention yet for tagging a pane with its pipeline role** (`researcher`, `worker`, `code-reviewer`, etc.) in a way `/panes` can read back. Currently `role` is always `None`. A real implementation likely needs each pane to call `cmux set-status` or similar with a recognizable key at spawn time — this is a director-skill-level concern (how the director tags panes it spawns), not something the dashboard backend can invent on its own. Flagging for Phase 3+ when the director skill and this endpoint need to agree on a convention.
- **`GET /log` does not yet stream** (BE-002's full requirement) — reads the whole file per request. Acceptable at current fixture scale; revisit once a real multi-feature log exists to benchmark against, per BE-052.

## What Phase 2 (frontend) can rely on

All 5 endpoints return the JSON shapes implied by `docs/implementation-specs.md` §4.1. `/panes` and `/stats` both degrade gracefully (no exceptions) on missing data — near-empty-state and cmux-unavailable-state are both exercised by the test suite, so the frontend's own empty-state handling (FE-040, FE-AC2) can be built and tested against real backend responses, not guessed at.
