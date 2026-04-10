# Skill: Write Tests

## Before writing

1. Read the source file you're testing — understand every function, its inputs, outputs, and edge cases
2. Read `.vibe/CONTEXT.md` for project constraints
3. Check if tests already exist in `tests/` for this module — extend, don't duplicate

## Test structure

- Class-based: `class TestFunctionName`
- Method names: `test_<scenario>` — describe the behavior, not the implementation
- One assertion focus per test
- No mocks — test real logic with real inputs
- Use `backend/seed_data.py` scenarios for realistic health data inputs

## What to test per module

### health_store.py
- All 20 metrics insert and retrieve correctly
- `get_summary()` returns correct avg/min/max/latest
- `get_trend()` returns correct direction (up/down/stable) and percentage
- `get_correlation()` returns valid Pearson coefficient
- `compare_periods()` returns correct averages for both periods
- Edge cases: empty DB, unknown metric, zero readings

### brain.py
- `build_system_message()` includes health context and user profile
- `build_system_message()` without profile falls back to "non disponible"
- `_execute_tool()` dispatches correctly to each of the 6 tools
- `_execute_tool()` returns valid JSON for all tools
- `_execute_tool()` with unknown tool returns error

### health_server.py
- `POST /health` accepts valid payload, returns count
- `POST /health` rejects empty metrics list
- `GET /health/summary` returns aggregated data
- `GET /health/ping` returns alive

## After writing

1. Run `uv run pytest <test_file> -v`
2. All tests must pass
3. If a test fails, fix the test (not the source code) unless you found a real bug
