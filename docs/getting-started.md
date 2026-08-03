# Getting started

This is the Claude-only spec-driven multi-agent development pipeline: one persistent **director** pane coordinates a feature's entire lifecycle — from a raw idea to an opened merge request — by spawning ephemeral Claude Code panes for each stage, running GitHub Spec Kit's phases, and stopping at nine human gates along the way. Nothing gets built past a gate you haven't explicitly approved, and nothing gets merged by the pipeline itself — the last thing it does is open a PR with a description you've approved.

## Where to go next

- **Scaffolding a new project?** → `docs/scaffolding-guide.md`
- **Want the full pipeline explained before running it?** → `docs/workflow-overview.md`
- **Ready to actually start the director and run a feature?** → `docs/working-with-the-director.md`
- **Sitting at an open gate right now, need to know what it's asking?** → `docs/human-gates.md`
- **Filling in `constitution.md`'s placeholders?** → `docs/constitution-authoring-guide.md`
- **Want the whole story, empty repo to ongoing feature delivery, in one read?** → `docs/lifecycle-walkthrough.md`
- **Trying to get the dashboard running?** → `docs/running-the-dashboard.md`
- **Want a technical overview, how-to guide, whitepaper, or other broad documentation written from the project's whole history?** → `docs/working-with-docs-synthesizer.md`

## The one-paragraph version

You hand the director a raw idea. It triages the feature as small or standard, then — for standard features — walks concept, architecture (with an independent critic pass), spec, and plan through their own gates, fanning out implementation to worker panes once you approve the plan. Every worker task runs in its own git worktree, tiered by cost (Haiku for small mechanical work, Sonnet as the default, Opus reserved for judgment-critical roles like the architecture critic, the code reviewer, and verification diagnosis) with automatic escalation on failure. Once every checkpoint passes, an independent code review and end-to-end verification run before docs and a PR description get drafted — each with its own gate. You approve at every step; the pipeline never decides for you.
