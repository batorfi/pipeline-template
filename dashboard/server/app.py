"""Dashboard backend — read-only, no gate authority, no outbound network calls.

Per the Dashboard runtime stack concept: serves factory-log.md, tasks.md, and
constitution.md as JSON to the static frontend. Never writes to any of those
files, never spawns a cmux pane, never makes a model call (BE-050, BE-051).

Run: uv run --with fastapi --with uvicorn --with pyyaml uvicorn app:create_app --factory
     (with PIPELINE_CONFIG pointing at dashboard/config.json)
"""

from __future__ import annotations

import os

from fastapi import FastAPI

from .app_config import DashboardConfig
from .routes import config as config_route
from .routes import log as log_route
from .routes import panes as panes_route
from .routes import stats as stats_route
from .routes import tasks as tasks_route


def create_app(config_path: str | None = None) -> FastAPI:
    app = FastAPI(title="Pipeline Dashboard Backend", docs_url="/docs")

    resolved_config_path = config_path or os.environ.get("PIPELINE_CONFIG")
    if not resolved_config_path:
        raise RuntimeError(
            "No config path given. Set PIPELINE_CONFIG to dashboard/config.json "
            "or pass config_path explicitly."
        )
    app.state.config = DashboardConfig.load(resolved_config_path)

    @app.middleware("http")
    async def no_cache_headers(request, call_next):
        # This dashboard's whole point is reflecting the project's current
        # state accurately — a stale cached copy of app.js/api.js served
        # from a browser's disk cache after a fix ships is worse than no
        # caching at all for a local dev tool like this. Confirmed as a
        # real source of confusion: a fix could be verified correct via
        # curl while the browser kept showing old behavior from a cached
        # static asset. Applies to both static files and API responses,
        # both of which should always be fresh here.
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        return response

    app.include_router(log_route.router)
    app.include_router(tasks_route.router)
    app.include_router(panes_route.router)
    app.include_router(config_route.router)
    app.include_router(stats_route.router)

    return app
