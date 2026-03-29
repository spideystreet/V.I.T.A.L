---
name: vibe
description: "Orchestrate Mistral Vibe as a worker agent from Claude Code. Use this skill when the user wants to delegate coding tasks to Vibe (implement features, write tests, fix bugs, refactor, write docs), review Vibe's work, or run Vibe in headless mode. Trigger on: 'use vibe', 'ask vibe to', 'delegate to vibe', 'vibe this', '/vibe', or any request to have Mistral Vibe do work."
argument-hint: "<task description for Vibe>"
---

# Skill: Vibe Orchestrator

Delegate tasks to Mistral Vibe (headless CLI) and review the results. Claude plans and reviews, Vibe executes.

## Architecture

```
User request
      │
Claude (main) ── breaks down into tasks
      │
  ┌───┴───┐          (parallel background Agents)
  │       │
Agent 1  Agent 2
  │       │
Plan     Plan       ← Claude crafts the Vibe prompt
Vibe     Vibe       ← Bash: vibe -p "..." --output json
Review   Review     ← Claude reads diff, runs tests
Fix/Retry Fix/Retry ← loop up to 2x if needed
  │       │
  └───┬───┘
      │
Claude (main) ── reports results to user
```

## Vibe agents

Three specialized Vibe agents are configured in `.vibe/agents/` (copy to `~/.vibe/agents/` on first setup):

| Agent | File | Use for | Key difference |
|-------|------|---------|----------------|
| `vital` | `vital.toml` | Docs, general tasks | `bash=ask`, `write_file=ask` |
| `vital-tests` | `vital-tests.toml` | Writing/fixing tests | All tools `always` (needs bash for pytest) |
| `vital-review` | `vital-review.toml` | Read-only review/audit | No write, no bash |

Select the agent with `--agent <name>`:

| Task type | Agent flag | Max turns | Max price |
|-----------|-----------|-----------|-----------|
| Docs | `--agent vital` | 10 | $0.30 |
| Tests | `--agent vital-tests` | 15 | $0.50 |
| Review/audit | `--agent vital-review` | 5 | $0.10 |

Vibe is scoped to docs and tests. For core implementation, Claude does it directly.

## Step 1: Break down and plan

Analyze the user's request. Split into independent tasks that can run in parallel. For each task, determine:
- Type (docs / tests / review)
- Target files
- Acceptance criteria

## Step 2: Launch background Agents

For each task, launch a background Agent with this template:

```
You are an orchestrator agent. Your job:

1. Launch Mistral Vibe headless to execute a task
2. Review the result
3. Fix or retry if needed (max 2 retries)

## Task for Vibe
<specific task description>

## Launch Vibe
Run this command (timeout 120000ms):

vibe -p "<prompt>. Do NOT run git commit, git add, or git push. Do NOT modify files outside the scope of this task." \
  --max-turns <N> \
  --max-price <P> \
  --output json \
  <--enabled-tools flags if restricted> \
  --workdir . \
  2>/dev/null | python3 -c "
import json, sys
msgs = json.load(sys.stdin)
assistant = [m for m in msgs if m.get('role') == 'assistant']
print(assistant[-1]['content'] if assistant else 'NO RESPONSE')
"

## After Vibe completes
1. Run: git diff --stat
2. Read each modified file
3. If tests: run uv run pytest <test_file> -v
4. Evaluate quality:
   - Code follows project conventions (class-based tests, English, no mocks)
   - All acceptance criteria met
   - Tests pass
5. If issues found:
   - Minor → fix directly yourself
   - Major → relaunch Vibe with corrected prompt (include what went wrong)
   - Max 2 retries, then report what's still broken

## Report back
Return a summary: what was done, what files changed, test results, any remaining issues.
```

## Step 3: Collect results

When background agents complete, Claude (main) receives notifications. Summarize results to the user:
- What each agent accomplished
- Files modified
- Test pass/fail status
- Any issues that need human attention

## Error handling

| Vibe output | Action |
|-------------|--------|
| Empty/no response | Retry once with same prompt |
| Timeout | Simplify task or increase max-turns |
| Bad quality | Agent fixes directly or retries with better prompt |
| Wrong files modified | `git checkout -- <file>`, retry with explicit constraints |
| Agent denied Bash | The user needs to approve the vibe command once, then it works |

## Example usage

User: "mets à jour les docs et tests pour health_store"

Claude breaks down into:
1. Agent (bg): Vibe updates `docs/apple-shortcut-setup.md` → Claude reviews
2. Agent (bg): Vibe writes/fixes `tests/test_health_store.py` → Claude reviews → runs pytest

Both run in parallel, user keeps working.

## Commit authorship rules

When committing work done via this skill, follow the authorship rules from `.claude/rules/authorship.md`.
