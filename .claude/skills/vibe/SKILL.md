---
name: vibe
description: "Delegate small, scoped tasks to Mistral Vibe from Claude Code. Use for writing tests, updating docs, or reviewing single files. Trigger on: 'use vibe', 'ask vibe to', 'delegate to vibe', 'vibe this', '/vibe'. Keep tasks scoped to 1-2 files max."
argument-hint: "<task scoped to 1-2 files>"
---

# Skill: Vibe Orchestrator

Delegate small tasks to Mistral Vibe (headless CLI). Claude crafts the prompt, launches vibe, parses the result, and reviews.

## What works

Vibe headless is reliable for **scoped tasks on 1-2 files**:
- Write/fix tests for a specific module
- Update a single doc file
- Review a single source file

## What does NOT work

- Large diffs (PR reviews, multi-file audits) — vibe crashes silently
- Background agents calling vibe — Bash permissions not propagated
- `--agent vital-review` with `bash=never` — can't run git diff

## How to run

Craft a clear, scoped prompt and launch vibe directly via Bash:

```bash
vibe -p "<prompt>. Do NOT run git commit, git add, or git push. Do NOT modify files outside the scope of this task." \
  --max-turns <N> \
  --max-price <P> \
  --output json \
  --workdir . \
  2>/dev/null | python3 -c "
import json, sys
msgs = json.load(sys.stdin)
assistant = [m for m in msgs if m.get('role') == 'assistant']
print(assistant[-1]['content'] if assistant else 'NO RESPONSE')
"
```

## Vibe agents

Configured in `.vibe/agents/` (copy to `~/.vibe/agents/` on first setup):

| Agent | Use for | Flags |
|-------|---------|-------|
| `vital` | Docs, general | `--agent vital` |
| `vital-tests` | Tests (needs bash for pytest) | `--agent vital-tests` |
| `vital-review` | Read-only review | `--agent vital-review` |

## Task sizing

| Task type | Max turns | Max price | Example |
|-----------|-----------|-----------|---------|
| Docs (1 file) | 10 | $0.30 | "update docs/apple-shortcut-setup.md" |
| Tests (1 module) | 15 | $0.50 | "write tests for health_store.py" |
| Review (1 file) | 5 | $0.20 | "review vital/config.py for issues" |

## After vibe completes

1. Check `git diff --stat` to see what changed
2. Read modified files to verify quality
3. If tests: run `uv run pytest <test_file> -v`
4. Decide:
   - **Good** — inform the user
   - **Minor issues** — fix directly
   - **Bad** — relaunch vibe with a corrected prompt (max 1 retry)

## Empty output troubleshooting

If vibe returns empty JSON, the task was too large or hit the budget. Split into smaller tasks.

## Commit authorship

Follow rules from `.claude/rules/authorship.md`.
