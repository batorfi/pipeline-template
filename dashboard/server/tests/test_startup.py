"""Implements BE-AC3: backend starts and serves successfully against a
fresh-scaffold near-empty state — tasks.md absent, factory-log.md header-only.
"""

from fastapi.testclient import TestClient

from dashboard.server.app import create_app


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
