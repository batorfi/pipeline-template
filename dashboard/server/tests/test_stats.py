"""Implements BE-AC2: /stats output matches a hand-computed expected result
against a fixture with a known escalation and restart pattern.
"""

from dashboard.server.readers.stats import compute_stats


def _entry(**kwargs):
    base = {"timestamp": "2026-01-01T00:00:00Z", "duration_seconds": 10}
    base.update(kwargs)
    return base


def test_hand_computed_escalation_and_restart():
    """One feature, small-triage: one worker task escalates once (Haiku -> Sonnet).
    One review restart on that same (small-triaged) feature.
    Expected: small escalation rate 100%, review restart rate 100%,
    small_triage_restart_count == 1.
    """
    entries = [
        _entry(timestamp="2026-01-01T00:00:00Z", stage="triage", feature="f1", triage_result="small"),
        _entry(
            timestamp="2026-01-01T00:01:00Z",
            stage="worker_task",
            feature="f1",
            tier="haiku",
            attempt=1,
            escalated_from=None,
            usage={"input_tokens": 100, "output_tokens": 50, "estimated_cost_usd": 0.01},
        ),
        _entry(
            timestamp="2026-01-01T00:02:00Z",
            stage="worker_task",
            feature="f1",
            tier="sonnet",
            attempt=2,
            escalated_from="haiku",
            usage={"input_tokens": 100, "output_tokens": 50, "estimated_cost_usd": 0.05},
        ),
        _entry(
            timestamp="2026-01-01T00:03:00Z",
            stage="review_gate",
            feature="f1",
            decision="restart",
            tier="opus",
            usage={"input_tokens": 500, "output_tokens": 200, "estimated_cost_usd": 0.30},
        ),
    ]

    stats = compute_stats(entries, opus_share_ceiling_pct=25.0)

    assert stats["escalation_rate_pct"]["small"] == 100.0
    assert stats["escalation_rate_pct"]["standard"] is None  # no standard-triage tasks at all
    assert stats["review_restart_rate_pct"] == 100.0
    assert stats["small_triage_restart_count"] == 1

    # cost: haiku 0.01, sonnet 0.05, opus 0.30 -> total 0.36
    assert stats["total_cost"] == 0.36
    assert stats["cost_by_tier"]["opus"] == 0.30
    # opus share = 0.30/0.36 = 83.3% > 25% ceiling
    assert stats["budget_trend"]["over_ceiling"] is True
    assert stats["budget_trend"]["opus_share_pct"] > 25.0


def test_no_entries_returns_zeroed_stats():
    stats = compute_stats([])
    assert stats["total_cost"] == 0
    assert stats["escalation_rate_pct"] == {"small": None, "standard": None}
    assert stats["review_restart_rate_pct"] is None
    assert stats["budget_trend"] is None  # no ceiling passed


def test_order_independence():
    """compute_stats must sort internally — passing entries newest-first
    (as /log does for display) must not change the result."""
    chronological = [
        _entry(timestamp="2026-01-01T00:00:00Z", stage="triage", feature="f1", triage_result="standard"),
        _entry(
            timestamp="2026-01-01T00:01:00Z",
            stage="worker_task",
            feature="f1",
            tier="sonnet",
            attempt=1,
            escalated_from=None,
            usage={"input_tokens": 1, "output_tokens": 1, "estimated_cost_usd": 0.01},
        ),
    ]
    newest_first = list(reversed(chronological))

    assert compute_stats(chronological)["escalation_rate_pct"] == compute_stats(newest_first)["escalation_rate_pct"]
