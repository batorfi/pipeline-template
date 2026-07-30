"""GET /stats — implements BE-040, BE-041."""

from __future__ import annotations

from fastapi import APIRouter, Query, Request

from ..readers.constitution_reader import read_constitution
from ..readers.log_reader import read_log
from ..readers.stats import compute_stats

router = APIRouter()


def _parse_pct(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return float(value.strip().rstrip("%"))
    except ValueError:
        return None


@router.get("/stats")
def get_stats(request: Request, feature: str | None = Query(default=None)):
    config = request.app.state.config
    log_result = read_log(config.factory_log_path, feature=feature)
    constitution = read_constitution(config.constitution_path)
    ceiling_pct = _parse_pct(constitution.get("budget", {}).get("opus_share_ceiling"))
    return compute_stats(log_result["entries"], opus_share_ceiling_pct=ceiling_pct)
