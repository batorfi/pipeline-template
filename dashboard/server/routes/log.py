"""GET /log — implements BE-001, BE-002."""

from __future__ import annotations

from fastapi import APIRouter, Query, Request

from ..readers.log_reader import read_log

router = APIRouter()


@router.get("/log")
def get_log(
    request: Request,
    feature: str | None = Query(default=None),
    limit: int | None = Query(default=None, ge=1),
):
    config = request.app.state.config
    return read_log(config.factory_log_path, feature=feature, limit=limit)
