"""GET /stats's aggregation logic — implements BE-040, BE-041.

Computes cost-by-tier, time-in-stage, gate-outcome counts, escalation rate,
review-restart rate, mitigation-round outcomes, and a triage-accuracy proxy
from already-parsed log entries. Pure function over a list of entry dicts —
no I/O here, so it's cheaply unit-testable against a hand-built fixture
(BE-AC2) without needing a real file on disk.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

GATE_STAGES = {
    "concept_gate",
    "architecture_gate",
    "spec_gate",
    "plan_gate",
    "checkpoint_gate",
    "review_gate",
    "verification_gate",
    "docs_gate",
    "pr_gate",
}


def compute_stats(entries: list[dict[str, Any]], opus_share_ceiling_pct: float | None = None) -> dict[str, Any]:
    # Must process in chronological order regardless of the order entries were
    # passed in — a triage entry has to be seen before the worker_task entries
    # it classifies, and callers (e.g. /log, which returns newest-first for
    # display) may hand this function entries in either order.
    entries = sorted(entries, key=lambda e: e.get("timestamp") or "")

    cost_by_tier: dict[str, float] = defaultdict(float)
    time_by_stage: dict[str, int] = defaultdict(int)
    gate_outcomes: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    escalations = {"small": 0, "standard": 0, "small_total": 0, "standard_total": 0}
    review_restarts = 0
    review_total = 0
    small_triage_restarts = 0
    mitigation_rounds: dict[int, int] = defaultdict(int)
    triage_results: dict[str, str] = {}  # feature -> "small"/"standard"

    for e in entries:
        tier = e.get("tier")
        usage = e.get("usage") or {}
        cost = usage.get("estimated_cost_usd")
        if tier and cost is not None:
            cost_by_tier[tier] += cost

        stage = e.get("stage")
        duration = e.get("duration_seconds")
        if stage and duration is not None:
            time_by_stage[stage] += duration

        if stage == "triage":
            feature = e.get("feature")
            result = e.get("triage_result")
            if feature and result:
                triage_results[feature] = result

        if stage in GATE_STAGES and e.get("decision") is not None:
            gate_outcomes[stage][e["decision"]] += 1

        if stage == "review_gate":
            review_total += 1
            if e.get("decision") == "restart":
                review_restarts += 1
                if triage_results.get(e.get("feature")) == "small":
                    small_triage_restarts += 1

        if stage == "verification_gate":
            round_num = e.get("mitigation_round", 0)
            if round_num:
                mitigation_rounds[round_num] += 1

        if stage == "worker_task":
            feature = e.get("feature")
            size = triage_results.get(feature)
            if e.get("attempt", 1) == 1:
                if size == "small":
                    escalations["small_total"] += 1
                elif size == "standard":
                    escalations["standard_total"] += 1
            if e.get("escalated_from"):
                if size == "small":
                    escalations["small"] += 1
                elif size == "standard":
                    escalations["standard"] += 1

    total_cost = sum(cost_by_tier.values())
    cost_by_tier_pct = {
        tier: (round(100 * amount / total_cost, 1) if total_cost else 0.0) for tier, amount in cost_by_tier.items()
    }

    opus_share_pct = cost_by_tier_pct.get("opus", 0.0)
    budget_trend = None
    if opus_share_ceiling_pct is not None:
        budget_trend = {
            "opus_share_pct": opus_share_pct,
            "ceiling_pct": opus_share_ceiling_pct,
            "over_ceiling": opus_share_pct > opus_share_ceiling_pct,
        }

    def _rate(numerator: int, denominator: int) -> float | None:
        return round(100 * numerator / denominator, 1) if denominator else None

    return {
        "cost_by_tier": dict(cost_by_tier),
        "cost_by_tier_pct": cost_by_tier_pct,
        "total_cost": round(total_cost, 4),
        "time_by_stage_seconds": dict(time_by_stage),
        "gate_outcomes": {k: dict(v) for k, v in gate_outcomes.items()},
        "escalation_rate_pct": {
            "small": _rate(escalations["small"], escalations["small_total"]),
            "standard": _rate(escalations["standard"], escalations["standard_total"]),
        },
        "review_restart_rate_pct": _rate(review_restarts, review_total),
        "small_triage_restart_count": small_triage_restarts,
        "mitigation_rounds_used": dict(mitigation_rounds),
        "budget_trend": budget_trend,
    }
