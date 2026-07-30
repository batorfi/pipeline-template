import json
from pathlib import Path

import pytest

FIXTURES_ROOT = Path(__file__).resolve().parents[3]  # pipeline-template/


@pytest.fixture
def pipeline_root() -> Path:
    return FIXTURES_ROOT


@pytest.fixture
def dashboard_config_file(tmp_path, pipeline_root):
    """A dashboard/config.json pointing at real fixture data, rooted correctly."""
    config_dir = pipeline_root / "dashboard"
    config_path = config_dir / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "factory_log_path": "factory-log/fixtures/all-stages-valid.md",
                "tasks_path": "does-not-exist-tasks.md",
                "constitution_path": "constitution/fixtures/fully-filled-valid.md",
            }
        ),
        encoding="utf-8",
    )
    yield config_path
    config_path.unlink(missing_ok=True)


@pytest.fixture
def near_empty_config_file(pipeline_root):
    config_dir = pipeline_root / "dashboard"
    config_path = config_dir / "config.near-empty.json"
    config_path.write_text(
        json.dumps(
            {
                "factory_log_path": "factory-log/fixtures/header-only-empty.md",
                "tasks_path": "does-not-exist-tasks.md",
                "constitution_path": "constitution/fixtures/fully-filled-valid.md",
            }
        ),
        encoding="utf-8",
    )
    yield config_path
    config_path.unlink(missing_ok=True)
