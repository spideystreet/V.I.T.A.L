# V.I.T.A.L — Context for Mistral Vibe

## Project overview

V.I.T.A.L (Voice-Integrated Tracker & Adaptive Listener) is a CLI Python health
assistant that receives Apple Watch data and provides voice-based health
conversations using Mistral LLM + Voxtral STT/TTS.

## Architecture

```
iPhone Shortcut (HealthKit) → POST /health → health_server.py → SQLite
CLI: audio.py → voxtral.py (STT) → brain.py (LLM) → voxtral.py (TTS) → viz.py
```

## Key files

- `vital/config.py` — env vars, constants, model IDs
- `vital/health_store.py` — SQLite storage
- `vital/health_server.py` — FastAPI receiver
- `vital/brain.py` — LLM system prompt + health context
- `vital/voxtral.py` — STT + streaming TTS
- `vital/audio.py` — mic recording
- `vital/viz.py` — terminal waveforms (Rich)
- `vital/main.py` — CLI orchestrator

## Constraints

- No medical diagnosis — always redirect to professionals
- No hardcoded secrets — env vars only
- Code and comments in English
- Conventional commits
- Terminal aesthetic: Mistral orange #ff7000

## How tasks work

Claude Code (main dev) writes task files in `.vibe/tasks/`.
Run a task: `vibe --prompt "Read .vibe/tasks/<task_file>.md and execute it"`
Each task has acceptance criteria — verify before marking done.
