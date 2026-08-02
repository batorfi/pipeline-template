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
        cmux_workspace_ids=None,
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


def test_feature_param_scopes_to_that_feature_even_when_it_is_not_the_newest(tmp_path):
    """Real bug: switching features in the dashboard's feature switcher never
    changed what /tasks returned, because resolve_tasks_path had no way to
    know which feature was selected -- it always used the most-recently-
    modified specs/*/tasks.md regardless. An explicit feature must win over
    the mtime heuristic, even for an older feature."""
    older = tmp_path / "specs" / "001-first-feature" / "tasks.md"
    older.parent.mkdir(parents=True)
    older.write_text("# older, but this is the one selected\n", encoding="utf-8")

    newer = tmp_path / "specs" / "002-second-feature" / "tasks.md"
    newer.parent.mkdir(parents=True)
    newer.write_text("# newer, not selected\n", encoding="utf-8")
    import os

    os.utime(newer, (older.stat().st_mtime + 10, older.stat().st_mtime + 10))

    config = _config(tmp_path, "specs/tasks.md")

    assert config.resolve_tasks_path(feature="001-first-feature") == older
    assert config.resolve_tasks_path(feature="002-second-feature") == newer
    # No feature given -> unchanged mtime-fallback behavior.
    assert config.resolve_tasks_path() == newer


def test_feature_param_with_no_matching_tasks_md_returns_none_not_another_feature(tmp_path):
    """An explicit, wrong/unfinished feature selection must not silently
    fall back to showing a different feature's tasks -- that would be
    exactly the original bug in a new disguise."""
    other = tmp_path / "specs" / "001-some-feature" / "tasks.md"
    other.parent.mkdir(parents=True)
    other.write_text("# some other feature's tasks\n", encoding="utf-8")

    config = _config(tmp_path, "specs/tasks.md")

    assert config.resolve_tasks_path(feature="002-not-started-yet") is None
