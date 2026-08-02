"""Implements BE-AC3: backend starts and serves successfully against a
fresh-scaffold near-empty state — tasks.md absent, factory-log.md header-only.
"""

import os

from fastapi.testclient import TestClient

from dashboard.server.app import create_app
from dashboard.server.app_config import DashboardConfig


def test_near_empty_state_all_endpoints_succeed(near_empty_config_file):
    app = create_app(config_path=str(near_empty_config_file))
    client = TestClient(app)

    log_response = client.get("/log")
    assert log_response.status_code == 200
    assert log_response.json() == {"entries": [], "errors": []}

    tasks_response = client.get("/tasks")
    assert tasks_response.status_code == 200
    assert tasks_response.json() == {"phases": []}

    stats_response = client.get("/stats")
    assert stats_response.status_code == 200
    assert stats_response.json()["total_cost"] == 0

    # /config and /panes don't depend on the log/tasks state at all — confirm
    # they still respond cleanly rather than erroring on an empty project.
    assert client.get("/config").status_code == 200
    assert client.get("/panes").status_code == 200


def test_responses_are_never_cached(near_empty_config_file):
    """Real bug: a fix could be verified correct via curl while a browser
    kept showing old behavior from a cached static app.js/api.js. Every
    response -- API and (when a StaticFiles mount is present) static assets
    alike -- must carry Cache-Control: no-store, since this dashboard's
    whole point is reflecting the project's current state accurately."""
    app = create_app(config_path=str(near_empty_config_file))
    client = TestClient(app)

    for path in ("/log", "/tasks", "/stats", "/config", "/panes"):
        response = client.get(path)
        assert response.headers.get("cache-control") == "no-store", path


def test_bare_relative_config_filename_resolves_correctly(dashboard_config_file, pipeline_root):
    """Regression test: PIPELINE_CONFIG=config.json (a bare filename, no
    directory component) must resolve project_root correctly. Path("config.json")
    .parent.parent stays "." without first calling .resolve() — this exact bug
    shipped and silently broke real usage (project_root collapsed to the cwd
    the process happened to start in, e.g. dashboard/ instead of the project
    root), even though every other test used an already-absolute config path
    and never exercised it."""
    original_cwd = os.getcwd()
    try:
        os.chdir(dashboard_config_file.parent)  # simulate `cd dashboard && ... PIPELINE_CONFIG=config.json`
        config = DashboardConfig.load(dashboard_config_file.name)  # bare filename, no directory
        assert config.project_root == pipeline_root.resolve()
        assert config.factory_log_path.exists()
        assert config.constitution_path.exists()
    finally:
        os.chdir(original_cwd)
