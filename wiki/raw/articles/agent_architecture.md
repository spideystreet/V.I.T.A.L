# Agent Architecture – Direct Mistral Orchestration (raw notes)

**Primary source**: https://www.linkedin.com/pulse/ai-agent-orchestration-healthcare-direct-mistral-frank-f1m7e
**Reading date**: 2026-04-07
**Status**: raw (do not modify)

---

## Blueprint – Direct Orchestration via Mistral API

- Multi-agent architecture in healthcare via Mistral API only
- **No LangChain, CrewAI or external orchestration framework**
- Sequential function calls (tool use / Mistral function calling)
- Context management: multi-turn conversation thread maintained manually

## Application for V.I.T.A.L

- Main agent: receives HealthKit data + user context → generates coaching
- Potential tools: getHealthData(), getUserHistory(), generateCoachingResponse(), triggerTTS()
- **No need for LangChain: Mistral API + function calling is sufficient**

## Status in V.I.T.A.L

**Already implemented** in `vital/brain.py` — one Mistral agent + 6 function-calling
tools (`get_health_summary`, `get_latest_readings`, `get_health_trend`,
`compare_periods`, `get_correlation`, `book_consultation`). No orchestration
framework needed. The "multi-agent" framing in the source article reduces to
exactly this pattern.

Future specialization (post-hackathon): a separate scoring agent for
deterministic burnout scores, and a background watcher (`vital/nudge.py`) for
proactive daily nudges.

## Benefits for the Hackathon

- Minimal and readable stack = easy to demo and explain to jury
- Full flow control: useful for fast debugging

## Unknown / To Confirm

- Does Mistral function calling support parallel tool calls?
- What is the typical latency of a Mistral Large call with tool use?