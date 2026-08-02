"""ensure_gitignore(): a scaffolded project previously got no .gitignore at
all, so .specify/cmux-workspaces.json (opaque, per-machine cmux IDs
meaningless on anyone else's machine) and dashboard/config.json (generated,
local) would get committed by default -- confirmed as a real, already-
shipped bug found already committed in a real scaffolded project three
features in.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scaffold"))

from scaffold import ensure_gitignore  # noqa: E402


def _clone_dir(pipeline_root: Path) -> Path:
    return pipeline_root  # scaffold/gitignore-additions.txt lives at <root>/scaffold/


def test_creates_gitignore_when_none_exists(tmp_path, pipeline_root):
    target = tmp_path / "project"
    target.mkdir()

    ensure_gitignore(_clone_dir(pipeline_root), target)

    gitignore = (target / ".gitignore").read_text(encoding="utf-8")
    assert ".specify/cmux-workspaces.json" in gitignore
    assert "dashboard/config.json" in gitignore
    assert "__pycache__/" in gitignore


def test_appends_only_missing_lines_to_existing_gitignore(tmp_path, pipeline_root):
    target = tmp_path / "project"
    target.mkdir()
    (target / ".gitignore").write_text("node_modules/\n.specify/cmux-workspaces.json\n", encoding="utf-8")

    ensure_gitignore(_clone_dir(pipeline_root), target)

    gitignore = (target / ".gitignore").read_text(encoding="utf-8")
    assert "node_modules/" in gitignore  # untouched
    assert gitignore.count(".specify/cmux-workspaces.json") == 1  # not duplicated
    assert "dashboard/config.json" in gitignore  # the actually-missing one got added


def test_idempotent_across_repeated_calls(tmp_path, pipeline_root):
    target = tmp_path / "project"
    target.mkdir()

    ensure_gitignore(_clone_dir(pipeline_root), target)
    first_pass = (target / ".gitignore").read_text(encoding="utf-8")

    ensure_gitignore(_clone_dir(pipeline_root), target)
    second_pass = (target / ".gitignore").read_text(encoding="utf-8")

    assert first_pass == second_pass
    assert second_pass.count("dashboard/config.json") == 1
