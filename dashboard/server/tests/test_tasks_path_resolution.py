"""DashboardConfig.resolve_tasks_path(): the configured tasks_path in
dashboard/config.json is a static value set once at scaffold time, but Spec
Kit creates each feature's tasks.md under a numbered per-feature directory
(specs/<NNN-feature-slug>/tasks.md) that doesn't exist yet at scaffold time
and changes with every new feature. A real dry run against this template
found the Task Board permanently empty because of exactly this staleness.
"""

from dashboard.server.app_config import DashboardConfig


def _config(tmp_path, tasks_path_value: str):
    return DashboardConfig(
        project_root=tmp_path,
        factory_log_path=tmp_path / "factory-log.md",
        tasks_path=(tmp_path / tasks_path_value) if tasks_path_value else None,
        constitution_path=tmp_path / "constitution.md",
        cmux_socket_path=None,
    )


def test_falls_back_to_most_recent_specs_tasks_md_when_configured_path_missing(tmp_path):
    older = tmp_path / "specs" / "001-first-feature" / "tasks.md"
    older.parent.mkdir(parents=True)
    older.write_text("# older\n", encoding="utf-8")

    newer = tmp_path / "specs" / "002-second-feature" / "tasks.md"
    newer.parent.mkdir(parents=True)
    newer.write_text("# newer\n", encoding="utf-8")
    # Force a distinct, later mtime regardless of filesystem timestamp resolution.
    import os

    os.utime(newer, (older.stat().st_mtime + 10, older.stat().st_mtime + 10))

    config = _config(tmp_path, "specs/tasks.md")  # the stale, never-real default

    assert config.resolve_tasks_path() == newer


def test_honors_configured_path_when_it_actually_exists(tmp_path):
    real = tmp_path / "specs" / "001-feature" / "tasks.md"
    real.parent.mkdir(parents=True)
    real.write_text("# real\n", encoding="utf-8")

    # A human deliberately pointed tasks_path at this file.
    config = _config(tmp_path, "specs/001-feature/tasks.md")

    assert config.resolve_tasks_path() == real


def test_returns_none_when_nothing_exists_anywhere(tmp_path):
    config = _config(tmp_path, "specs/tasks.md")
    assert config.resolve_tasks_path() is None
