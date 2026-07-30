"""GET /panes — implements BE-020, BE-021."""

from __future__ import annotations

from fastapi import APIRouter, Request

from ..readers.panes_reader import read_panes

router = APIRouter()


@router.get("/panes")
def get_panes(request: Request):
    config = request.app.state.config
    return read_panes(socket_path=config.cmux_socket_path)
