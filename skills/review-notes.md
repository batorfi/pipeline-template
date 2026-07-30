# Skill review notes — Phase 0, T009–T019

Review pass against: trigger-accurate frontmatter `description`, output-shape compatibility with the next role's stated inputs, and (director only) critique #4.

## director (T009)

Two real issues found and fixed directly in `drafts/skills/director/SKILL.md`:
1. **Stale path.** Referenced `concepts/20260720-101336_...` — the published concept moved to `concepts/claude-only-pipeline/20260720-101336_...` when the concept family was reorganized. Fixed.
2. **Singular concurrency-cap language.** The constitution now has both a per-feature cap and a project-wide aggregate cap (CONST-020/021, added to close critique #6). The skill's startup checklist and fan-out step only referenced "the" cap, singular. Fixed in both places.
3. **`triage_result` vs. `decision` conflation.** Building the factory-log fixtures (T003) surfaced that triage's small/standard classification isn't a gate decision and shouldn't use the `decision` field (LOG-025 was added to the schema to fix this). The director skill's triage step said "log the triage decision" — updated to reference `triage_result` explicitly and note it's not a gate decision.

**Critique #4 disposition (no independent check on the director's own triage/restart judgment):** confirmed as an accepted v1 limitation, per `docs/implementation-plan.md` §10. No guardrail added to the skill. Revisit after the Phase 5 pilot if triage misclassification turns out to be a recurring real problem rather than theoretical.

## researcher, concept-writer, architecture-designer, architecture-critic, adr-maker, worker, code-reviewer, verifier, techwriter, pr-writer (T010–T019)

All ten reviewed for: trigger-accurate `description` (confirmed — each names its specific spawn trigger and an explicit "do not use for X" boundary), and output-shape compatibility with the next consumer in the chain (confirmed by cross-reading — e.g., researcher's five-heading `context.md` matches what concept-writer and architecture-designer say they read; architecture-critic's `critique.md` structure matches what architecture-designer says it processes on a polish round; verifier's diagnosis-then-mitigation split matches the director's own description of that step).

No changes needed. All ten accepted as-is.

## Net result

Phase 0 (T001–T020) complete. One schema bug (triage_result) and one skill bug (stale path + singular-cap language) found and fixed as a direct result of doing this review pass for real rather than rubber-stamping it — validates the discipline of dry-testing before bundling into the template repo, per the scaffold concept's own guidance.
