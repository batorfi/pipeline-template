# Dashboard frontend — Phase 2 notes

Vanilla HTML/CSS/JS, no build step, ES modules. 9 files: `index.html`, `assets/theme.css`, `assets/layout.css`, and 7 JS modules (`api.js`, `gates.js`, `attention-band.js`, `step-reports.js`, `task-board.js`, `totals-panel.js`, `feature-switcher.js`, `app.js`). `live-panes.js` (the "Running Now" zone) was removed by request — see CHANGELOG.

## What's actually verified

- **Static serving**: every file confirmed served correctly (HTTP 200) via a local `python -m http.server` — no 404s, no path errors.
- **Backend data contract**: every zone's render function consumes exactly the JSON shapes Phase 1's endpoints return, confirmed by cross-reading both sides while writing this code (not by execution, see below).
- **Zero external calls**: confirmed by grep — no CDN references, no external URLs anywhere in `index.html` or `assets/`; the only `fetch()` call in the codebase is same-origin (`api.js`).
- **A real backend bug caught while building this**: `/log` entries only carried frontmatter, not the prose summary the step-report feed needs to display (LOG-002 requires every entry to have prose; nothing was surfacing it to consumers). Fixed in `factory-log/validator.py` (synthesizes a `summary` key from the prose body) and `factory-log/SCHEMA.md` §2.5, with a new regression test (`test_entries_carry_prose_summary`) in the Phase 1 suite. All 12 backend tests still pass after the fix.

## What's honestly NOT verified

**No JavaScript in this codebase has actually been executed.** This environment has neither Node nor a browser available, so `FE-AC1` (fixture-data mode against all zone states) and `FE-AC2` (`panes_unavailable` graceful degradation) are verified only at the level of "the code reads correctly and the data contracts match" — not "I watched it render correctly." T039 and T040 are marked complete on that basis, which is weaker than the acceptance criteria technically call for (a real visual check). If a bug exists in the DOM-manipulation logic itself (a typo in a selector, an off-by-one in the loop-collapsing logic), nothing in this build process would have caught it.

**T041 (cmux's actual embedded browser) is honestly left incomplete** — it requires a live cmux instance, which isn't available here. This was flagged as a real blocking unknown from the start (`docs/implementation-specs.md` §7) and stays that way. Do not mark it done without actually opening this page in cmux and confirming: the `file://`/CSP behavior questions from the runtime-stack concept, and that the layout/interactions genuinely work as designed.

## Recommended first real step once cmux is available

1. Point cmux's embedded browser at `dashboard/index.html` served via a local static server (per the runtime-stack concept's fallback plan — `file://` behavior is still unconfirmed).
2. Run the backend against the `all-stages-valid.md` / `fully-filled-valid.md` fixtures (same ones the pytest suite uses) so the dashboard has real, known data to render against.
3. Visually check all 4 zones render as designed, especially the attention band's gate-open state (never actually seen rendered) and the loop-collapsing `<details>` group in the step-report feed.
4. Only then mark T041 and fully re-confirm T039/T040 against what was actually observed, not inferred from code review.
