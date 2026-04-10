# Skill: Update Docs

## Which docs to update

- `.vibe/CONTEXT.md` — Vibe's view of the project. Update when code structure changes.
- `docs/health-metrics.md` — metric dictionary. Update when metrics are added/removed.
- `docs/privacy-rgpd.md` — privacy doc. Update when data flow changes.
- `docs/plan-hackathon.md` — hackathon plan. Update when scope/timeline changes.

## Rules

- Keep the **burnout/stress framing** — V.I.T.A.L is a burnout prevention tool, not a generic health app
- Never modify `CLAUDE.md` — that's Claude Code's domain
- Never modify `.claude/` files
- Match the existing tone and format of each doc
- English for code docs, French allowed for pitch-facing docs (`plan-hackathon.md`, `pitch-stats.md`)
- Keep docs concise — no filler, no redundancy

## When updating CONTEXT.md

- Check current file count in `backend/`
- Verify the tool count (currently 6 tools in brain.py)
- Verify the metric count (currently 20 in health_store.py)
- Update architecture diagram if endpoints changed

## When updating health-metrics.md

- Cross-check with `_DEFAULT_METRICS` in `health_store.py`
- Keep the table format: metric | unit | description

## After updating

- Read the file back to verify formatting
- Run `uv run ruff check backend/` to ensure no code was accidentally modified
