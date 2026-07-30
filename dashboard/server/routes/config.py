"""GET /config — implements BE-030."""

from __future__ import annotations

from fastapi import APIRouter, Request

from ..readers.constitution_reader import read_constitution

router = APIRouter()


@router.get("/config")
def get_config(request: Request):
    config = request.app.state.config
    return read_constitution(config.constitution_path)
