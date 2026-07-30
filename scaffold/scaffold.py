"""scaffold.py — turns a brand-new (or existing) repository into one ready to
run its first feature through the Claude-only pipeline. Implements SCAF-000
through SCAF-011 (see docs/implementation-specs.md §6).

Fresh scaffold:  scaffold.py --template-version <tag> --target <path>
Sync existing:   scaffold.py --sync --template-version <tag> --target <path>

Steps 1-7(+7a) below are mechanized here. Steps 8-9 (the dry-run synthetic
feature and its recalibration) are deliberately NOT automated — see
docs/scaffolding-guide.md.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from render import render_constitution, render_entry_zero
from validate_constitution import validate_constitution

TEMPLATE_REPO = "batorfi/pipeline-template"
TEMPLATE_REPO_URL = f"https://github.com/{TEMPLATE_REPO}.git"


class ScaffoldError(Exception):
    """A fatal, expected failure — printed cleanly, no partial state left behind
    where avoidable (SCAF-002)."""


# ---------------------------------------------------------------------------
# Step: clone at a pinned tag (SCAF-000, SCAF-001 clone portion)
# ---------------------------------------------------------------------------
#
# The template repository is public, so this needs no authentication at all —
# a plain, anonymous `git clone` works. If `gh` happens to be installed and
# authenticated, prefer it (marginally more resilient behind some corporate
# proxies/mirrors that intercept plain git but allow the GitHub API), but
# fall back to plain git rather than requiring gh — a curl-piped installer
# with no gh available must still work.

def clone_template(template_version: str, dest: Path) -> Path:
    clone_dir = dest / "_template_clone"

    gh_available = shutil.which("gh") is not None
    if gh_available:
        result = subprocess.run(
            ["gh", "repo", "clone", TEMPLATE_REPO, str(clone_dir), "--", "--branch", template_version, "--depth", "1"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return clone_dir
        # Fall through to plain git on any gh failure (including "not authenticated") —
        # the repo is public, plain git doesn't need what gh failed on.

    result = subprocess.run(
        ["git", "clone", "--branch", template_version, "--depth", "1", TEMPLATE_REPO_URL, str(clone_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.lower()
        if "not found" in stderr or "could not find remote branch" in stderr or "reference is not a tree" in stderr:
            raise ScaffoldError(
                f"Template version '{template_version}' not found in {TEMPLATE_REPO}. "
                f"Check the tag exists: https://github.com/{TEMPLATE_REPO}/tags"
            )
        raise ScaffoldError(f"Clone of {TEMPLATE_REPO}@{template_version} failed:\n{result.stderr}")

    return clone_dir


# ---------------------------------------------------------------------------
# Step: copy skills/dashboard/specs-README/docs (SCAF-001 copy portion)
# ---------------------------------------------------------------------------

def copy_tree_atomic(src: Path, dst: Path) -> None:
    """Copy src -> dst, failing loudly and leaving no partial dst on error
    (SCAF-002) by copying to a temp sibling first, then renaming into place."""
    if not src.exists():
        raise ScaffoldError(f"Expected source path does not exist: {src}")

    tmp_dst = dst.parent / f".{dst.name}.scaffold-tmp"
    if tmp_dst.exists():
        shutil.rmtree(tmp_dst)

    try:
        shutil.copytree(src, tmp_dst)
    except OSError as e:
        raise ScaffoldError(f"Failed copying {src} -> {dst}: {e}") from e

    if dst.exists():
        shutil.rmtree(dst)
    tmp_dst.rename(dst)


CONFLICTING_PATHS = ("dashboard", "docs")  # generic names an existing project may already own


def check_no_conflicting_existing_content(target: Path) -> None:
    """Fresh scaffold refuses to run if the target already has non-empty
    dashboard/ or docs/ directories — copy_tree_atomic's destructive
    shutil.rmtree(dst) would otherwise silently delete an existing project's
    own content with those names. This check exists specifically for
    scaffolding INTO an existing codebase, not just an empty directory —
    an empty/fresh target never trips it. Caught during a documentation
    pass, not a test run: worth being honest that this was found by
    thinking through the "existing project" case, not by exercising it."""
    conflicts = []
    for name in CONFLICTING_PATHS:
        p = target / name
        if p.exists() and any(p.iterdir()):
            conflicts.append(name)

    if conflicts:
        listed = ", ".join(f"'{c}/'" for c in conflicts)
        raise ScaffoldError(
            f"Target already has non-empty {listed} — scaffolding would silently delete and "
            "replace it (this pipeline's own dashboard/docs use those same directory names). "
            "Move or rename your existing directory first, then re-run scaffold, or scaffold "
            "into a subdirectory instead of your project's root."
        )


def do_copy_steps(clone_dir: Path, target: Path) -> None:
    copy_tree_atomic(clone_dir / "skills", target / ".claude" / "skills-pipeline-roles")
    copy_tree_atomic(clone_dir / "dashboard", target / "dashboard")

    specs_dir = target / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(clone_dir / "specs" / "README-template.md", specs_dir / "README.md")

    copy_tree_atomic(clone_dir / "docs", target / "docs")

    # The setup-cmux-workspaces / run-dashboard-in-pane prompts live only in
    # this template repo's own scaffold/prompts/ — without copying them into
    # the scaffolded project, a developer following the printed checklist has
    # nowhere to actually find them after scaffold.sh exits.
    copy_tree_atomic(clone_dir / "scaffold" / "prompts", target / "docs" / "prompts")

    # dashboard/server/readers/_factory_log_validator.py loads
    # factory-log/validator.py by a fixed path relative to the project root
    # at runtime (parents[3] from its own file) — without copying validator.py
    # (and SCHEMA.md, which it documents itself against) into the scaffolded
    # project, the dashboard backend fails to import at all.
    factory_log_dir = target / "factory-log"
    factory_log_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(clone_dir / "factory-log" / "validator.py", factory_log_dir / "validator.py")
    shutil.copy2(clone_dir / "factory-log" / "SCHEMA.md", factory_log_dir / "SCHEMA.md")


def write_dashboard_config(target: Path) -> None:
    # docs/running-the-dashboard.md documents dashboard/config.json as
    # "generated by scaffold.sh, not hand-written" — but nothing here ever
    # actually generated it, so every scaffolded project's dashboard backend
    # failed at startup with FileNotFoundError until a human wrote this file
    # by hand. tasks_path points at a file that doesn't exist yet on a fresh
    # scaffold; per dashboard/config.schema.json (BE-AC3) that's valid,
    # tracked-empty state, not an error.
    config = {
        "factory_log_path": ".specify/factory-log.md",
        "tasks_path": "specs/tasks.md",
        "constitution_path": ".specify/memory/constitution.md",
        "cmux_socket_path": None,
    }
    config_path = target / "dashboard" / "config.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Step: render constitution + factory-log (SCAF-001 render portion)
# ---------------------------------------------------------------------------

def get_spec_kit_version() -> str | None:
    if not shutil.which("specify"):
        return None
    result = subprocess.run(["specify", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def do_render_steps(clone_dir: Path, target: Path, template_version: str, spec_kit_version: str | None) -> Path:
    specify_memory = target / ".specify" / "memory"
    specify_memory.mkdir(parents=True, exist_ok=True)

    constitution_template = (clone_dir / "constitution" / "constitution.template.md").read_text(encoding="utf-8")
    rendered_constitution = render_constitution(constitution_template, template_version, spec_kit_version)
    constitution_path = specify_memory / "constitution.md"
    constitution_path.write_text(rendered_constitution, encoding="utf-8")

    header = (clone_dir / "factory-log" / "header-template.md").read_text(encoding="utf-8")
    entry_zero_template = (clone_dir / "factory-log" / "entry-zero-template.md").read_text(encoding="utf-8")
    entry_zero = render_entry_zero(entry_zero_template, template_version, spec_kit_version)

    factory_log_path = target / ".specify" / "factory-log.md"
    factory_log_path.write_text(header + entry_zero, encoding="utf-8")

    return constitution_path


# ---------------------------------------------------------------------------
# Step: specify init (SCAF-001 final portion)
# ---------------------------------------------------------------------------

def run_specify_init(target: Path) -> bool:
    specify_bin = shutil.which("specify")
    if not specify_bin:
        print(
            "WARNING: `specify` (GitHub Spec Kit CLI) not found on PATH — skipping "
            "`specify init`. Install it and run `specify init . --integration claude` "
            "manually in the target repo before running a feature.",
            file=sys.stderr,
        )
        return False

    # By the time this runs, the target is already non-empty — scaffold.py's
    # own copy steps have already populated it (skills, dashboard, docs,
    # specs, .specify/). `specify init` detects that and asks an interactive
    # "Current directory is not empty ... continue? [y/N]" question. When
    # scaffold.sh is run non-interactively (e.g. via `curl | bash`, which has
    # no TTY attached), that prompt has nothing to read from stdin and the
    # process fails immediately with an unhelpful, often-empty error —
    # exactly the failure this was originally written to just warn-and-skip
    # on. Feeding "y" via `input=` answers that one prompt directly, so the
    # automated path can actually succeed instead of always needing the
    # manual fallback.
    #
    # Not yet verified against a real `specify` install in this repo's own
    # testing (no `specify` binary was available in the environment this was
    # built and tested in) — if `specify init` still prompts for something
    # else beyond the non-empty-directory confirmation (e.g. an interactive
    # coding-agent-integration menu not fully bypassed by --integration
    # claude), this single "y\n" may not be sufficient. Report back if it
    # isn't.
    result = subprocess.run(
        ["specify", "init", ".", "--integration", "claude"],
        cwd=target,
        input="y\n",
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"WARNING: `specify init` failed:\n{result.stderr}\nContinuing — run it manually.", file=sys.stderr)
        return False
    return True


# ---------------------------------------------------------------------------
# Step: <<FILL:...>> validation gate (SCAF-003)
# ---------------------------------------------------------------------------

def check_constitution_ready(constitution_path: Path) -> bool:
    result = validate_constitution(constitution_path.read_text(encoding="utf-8"))
    if result.ok:
        return True

    print("\nConstitution is NOT ready — scaffolding is not complete:", file=sys.stderr)
    print(result.report(), file=sys.stderr)
    return False


# ---------------------------------------------------------------------------
# Fresh scaffold orchestration
# ---------------------------------------------------------------------------

def scaffold(template_version: str, target: str) -> int:
    target_path = Path(target).resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    existing_constitution = target_path / ".specify" / "memory" / "constitution.md"
    if existing_constitution.exists():
        raise ScaffoldError(
            f"{existing_constitution} already exists — this target looks already scaffolded. "
            "Re-running a fresh scaffold here would silently overwrite any values you've already "
            "filled in (SCAF-AC2 requires this NOT happen). Use `--sync` instead, which preserves "
            "your existing constitution values and only merges in new required sections."
        )

    check_no_conflicting_existing_content(target_path)

    if not (target_path / ".git").exists():
        subprocess.run(["git", "init"], cwd=target_path, check=True, capture_output=True)
        print(f"Initialized git repository at {target_path}")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            clone_dir = clone_template(template_version, Path(tmp))
            do_copy_steps(clone_dir, target_path)
            write_dashboard_config(target_path)
            spec_kit_version = get_spec_kit_version()
            constitution_path = do_render_steps(clone_dir, target_path, template_version, spec_kit_version)
            specify_ran = run_specify_init(target_path)
        except ScaffoldError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

    ready = check_constitution_ready(constitution_path)

    specify_note = (
        f"\n  NOTE: `specify init` was not run automatically (see warning above).\n"
        f"  Run these two commands — in this exact order — to do it manually:\n"
        f"    cd {target_path}\n"
        f"    specify init . --integration claude\n"
        f"  Running `specify init` from any OTHER directory (e.g., the parent you\n"
        f"  ran this scaffold command from) will install Spec Kit there instead —\n"
        f"  a real mistake that has happened before. The `cd` above is not optional."
        if not specify_ran
        else ""
    )

    print(f"""
Scaffold complete at {target_path}.

Manual steps remaining — run every command below from inside {target_path},
never from its parent directory:

  1. Fill in every <<FILL:...>> marker in .specify/memory/constitution.md
     {'(none remain)' if ready else '(see the list above — scaffold is NOT ready until these are resolved)'}
  2. Stand up the 3 core cmux workspaces (main, design, implementation) — see
     docs/prompts/setup-cmux-workspaces.md (paste its prompt into a Claude
     Code session running inside cmux, in your intended main workspace).
  3. Start the dashboard backend and confirm the frontend renders — see
     docs/prompts/run-dashboard-in-pane.md and docs/running-the-dashboard.md.
  4. Run one deliberately trivial synthetic feature through all 9 gates by
     hand, approving explicitly at every gate. This is a genuine confidence
     check — do not skip it. See docs/working-with-the-director.md for how
     to actually start the director and respond at a gate (the dashboard
     is read-only — you respond in the director's own chat, not there).
  5. Revisit the concurrency caps and budget figures using what that dry run
     actually logged.
{specify_note}
""")

    return 0 if ready else 1


# ---------------------------------------------------------------------------
# --sync: update an already-scaffolded project (SCAF-010, SCAF-011)
# ---------------------------------------------------------------------------

def _diff_file_lists(old_dir: Path, new_dir: Path) -> dict[str, list[str]]:
    old_files = {str(p.relative_to(old_dir)) for p in old_dir.rglob("*") if p.is_file()} if old_dir.exists() else set()
    new_files = {str(p.relative_to(new_dir)) for p in new_dir.rglob("*") if p.is_file()}
    return {
        "added": sorted(new_files - old_files),
        "removed": sorted(old_files - new_files),
        "changed": sorted(
            f
            for f in old_files & new_files
            if (old_dir / f).read_bytes() != (new_dir / f).read_bytes()
        ),
    }


def _print_sync_preview(label: str, diff: dict[str, list[str]]) -> None:
    total = len(diff["added"]) + len(diff["removed"]) + len(diff["changed"])
    print(f"\n{label}: {total} file(s) will change")
    for f in diff["added"]:
        print(f"  + {f}")
    for f in diff["removed"]:
        print(f"  - {f}")
    for f in diff["changed"]:
        print(f"  ~ {f}")


def _merge_constitution(existing_text: str, new_template_text: str) -> str:
    """Structural merge, per the template-repo concept's sync procedure:
    never touch the human's existing filled-in values; only add a new
    required section (as a flagged placeholder) if the new template
    introduces one the existing file doesn't have."""
    existing_headings = set(re.findall(r"^##\s+(.+?)\s*$", existing_text, re.MULTILINE))

    new_sections = re.split(r"(?=^##\s+.+$)", new_template_text, flags=re.MULTILINE)
    appended = []
    for section in new_sections:
        m = re.match(r"^##\s+(.+?)\s*$", section, re.MULTILINE)
        if not m:
            continue
        heading = m.group(1).strip()
        if heading not in existing_headings and heading != "Pipeline template version":
            appended.append(section.rstrip() + "\n")

    if not appended:
        return existing_text

    addition_header = "\n\n<!-- Sections added by --sync, previously absent from this constitution. Fill in any <<FILL:...>> markers below. -->\n\n"
    return existing_text.rstrip() + addition_header + "\n".join(appended)


def sync(template_version: str, target: str) -> int:
    target_path = Path(target).resolve()
    if not target_path.exists():
        raise ScaffoldError(f"--sync target does not exist: {target_path}")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            clone_dir = clone_template(template_version, Path(tmp))
        except ScaffoldError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1

        print(f"Sync preview: {TEMPLATE_REPO}@{template_version} -> {target_path}\n(nothing has been changed yet)")

        skills_diff = _diff_file_lists(target_path / ".claude" / "skills-pipeline-roles", clone_dir / "skills")
        dashboard_diff = _diff_file_lists(target_path / "dashboard", clone_dir / "dashboard")
        docs_diff = _diff_file_lists(target_path / "docs", clone_dir / "docs")
        _print_sync_preview("skills/", skills_diff)
        _print_sync_preview("dashboard/", dashboard_diff)
        _print_sync_preview("docs/", docs_diff)

        constitution_path = target_path / ".specify" / "memory" / "constitution.md"
        if constitution_path.exists():
            new_template = (clone_dir / "constitution" / "constitution.template.md").read_text(encoding="utf-8")
            merged_preview = _merge_constitution(constitution_path.read_text(encoding="utf-8"), new_template)
            added_len = len(merged_preview) - len(constitution_path.read_text(encoding="utf-8"))
            print(f"\nconstitution.md: {'no new required sections' if added_len == 0 else f'{added_len} chars of new required sections will be appended (existing values untouched)'}")

        print("\nfactory-log.md: never touched by sync.")

        response = input("\nApply this sync? [y/N] ").strip().lower()
        if response != "y":
            print("Sync cancelled — nothing changed.")
            return 0

        # Wholesale overwrite: skills, dashboard, docs (SCAF-010)
        copy_tree_atomic(clone_dir / "skills", target_path / ".claude" / "skills-pipeline-roles")

        # dashboard/config.json isn't part of the template's own dashboard/
        # tree (it's generated per project, by write_dashboard_config below)
        # — copy_tree_atomic replaces target/dashboard/ wholesale, which would
        # silently delete an existing config.json. Preserve it across sync,
        # same discipline as constitution.md's values below.
        existing_dashboard_config = target_path / "dashboard" / "config.json"
        preserved_config = existing_dashboard_config.read_text(encoding="utf-8") if existing_dashboard_config.exists() else None

        copy_tree_atomic(clone_dir / "dashboard", target_path / "dashboard")

        if preserved_config is not None:
            existing_dashboard_config.write_text(preserved_config, encoding="utf-8")
        else:
            write_dashboard_config(target_path)

        copy_tree_atomic(clone_dir / "docs", target_path / "docs")
        copy_tree_atomic(clone_dir / "scaffold" / "prompts", target_path / "docs" / "prompts")

        factory_log_dir = target_path / "factory-log"
        factory_log_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(clone_dir / "factory-log" / "validator.py", factory_log_dir / "validator.py")
        shutil.copy2(clone_dir / "factory-log" / "SCHEMA.md", factory_log_dir / "SCHEMA.md")

        # Structural merge: constitution (SCAF-010)
        if constitution_path.exists():
            new_template = (clone_dir / "constitution" / "constitution.template.md").read_text(encoding="utf-8")
            merged = _merge_constitution(constitution_path.read_text(encoding="utf-8"), new_template)
            constitution_path.write_text(merged, encoding="utf-8")

    print(f"\nSync complete. Update the version-pin block in {constitution_path} to record the new template version and sync date.")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-version", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--sync", action="store_true", help="Update an already-scaffolded project instead of scaffolding a new one.")
    args = parser.parse_args(argv[1:])

    try:
        if args.sync:
            return sync(args.template_version, args.target)
        return scaffold(args.template_version, args.target)
    except ScaffoldError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
