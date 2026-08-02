"""GET /tasks — implements BE-010."""

from __future__ import annotations

from fastapi import APIRouter, Request

from ..readers.tasks_reader import read_tasks

router = APIRouter()


@router.get("/tasks")
def get_tasks(request: Request, feature: str | None = None):
    config = request.app.state.config
    return read_tasks(config.resolve_tasks_path(feature=feature))
