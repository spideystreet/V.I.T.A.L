# Skill: Audit Python

## Checklist

### Error handling at system boundaries
- [ ] Database calls (`health_store.py`) — what happens if PostgreSQL is down?
- [ ] Mistral API calls (`brain.py`, `voxtral.py`) — what happens if the API is unreachable or returns an error?
- [ ] Tool execution (`_execute_tool`) — what happens if a tool raises an exception?
- [ ] FastAPI endpoints — are HTTP errors returned with proper status codes?

### Data integrity
- [ ] All 20 metrics are in `_DEFAULT_METRICS` and match `MetricType` Swift enum
- [ ] `get_summary()`, `get_trend()`, `get_correlation()`, `compare_periods()` handle empty results
- [ ] No division by zero in `get_trend()` or `get_correlation()`
- [ ] SQL queries are parameterized (no injection risk)

### Code quality
- [ ] No unused imports
- [ ] No hardcoded secrets (API keys, passwords, DB names)
- [ ] Consistent naming (snake_case functions/vars)
- [ ] No dead code or commented-out blocks
- [ ] Docstrings on public functions

### LLM tool use
- [ ] All 6 tools defined in `TOOLS` list match `_execute_tool()` dispatch
- [ ] Tool descriptions are clear enough for the LLM to choose correctly
- [ ] Tool parameter types match what the functions expect
- [ ] `book_consultation` is clearly simulated (not real booking)

### Security
- [ ] `.env` is in `.gitignore`
- [ ] No secrets in code, config files, or seed data
- [ ] No PII in system prompt or health context sent to Mistral

## Output format

Report findings as:
```
file.py:line — [severity] description
```
Severity: CRITICAL / WARNING / INFO

Do NOT modify files unless explicitly asked. This is a read-only audit by default.
