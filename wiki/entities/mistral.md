---
title: Mistral AI
created: 2026-04-07
updated: 2026-04-10
type: entity
tags: [llm, partner, tech, api-reference]
sources:
  - docs.mistral.ai
  - mistral_health.md
  - agent_architecture.md
  - voxtral_tts.md
---

# Mistral AI

## Overview

European LLM provider, native GDPR compliance, FR/EU data sovereignty.

## Models (April 2026)

| Model | API ID | Alias | Params (total/active) | Context | Cost (in/out per 1M tok) |
|-------|--------|-------|-----------------------|---------|--------------------------|
| **Large 3** | `mistral-large-2512` | `mistral-large-latest` | 675B / 41B (MoE) | 256k | $0.50 / $1.50 |
| **Medium 3.1** | `mistral-medium-2508` | `mistral-medium-latest` | closed | 128k | $0.40 / $2.00 |
| **Small 4** | `mistral-small-2603` | `mistral-small-latest` | 119B / 6.5B (MoE) | 256k | $0.15 / $0.60 |

All support: function calling, streaming, structured output, agents/conversations API.

**V.I.T.A.L uses:** `mistral-large-latest` (LLM) + `voxtral-mini-transcribe-2507` (STT) + `voxtral-mini-tts-2603` (TTS)

## API Reference

### Base
- **URL:** `https://api.mistral.ai`
- **Auth:** `Authorization: Bearer <MISTRAL_API_KEY>`
- **SDK:** `pip install mistralai`

### Chat Completions — `POST /v1/chat/completions`

```json
{
  "model": "mistral-large-latest",
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."}
  ],
  "tools": [...],
  "tool_choice": "auto",
  "stream": true,
  "temperature": 0.3
}
```

**tool_choice values:** `"auto"` (default), `"none"`, `"any"` / `"required"`, `{"type": "function", "function": {"name": "..."}}`

**Tool definition:**
```json
{
  "type": "function",
  "function": {
    "name": "get_health_summary",
    "description": "Aggregated health metrics over a time window",
    "parameters": {
      "type": "object",
      "properties": {"hours": {"type": "integer"}},
      "required": ["hours"]
    }
  }
}
```

**Tool call response:** `finish_reason: "tool_calls"`, then send `ToolMessage` back with `tool_call_id`.

### STT — `POST /v1/audio/transcriptions`

- Models: `voxtral-mini-transcribe-2507`, `voxtral-mini-transcribe-realtime-2602`
- Input: multipart/form-data (`file`) or `file_url`
- Params: `language` (e.g. `"fr"`), `diarize`, `timestamp_granularities`
- Streaming: SSE with `transcription.text.delta` events
- Realtime: WebSocket-like protocol with `input_audio.append` (base64 PCM chunks)

### TTS — `POST /v1/audio/speech`

- Model: `voxtral-mini-tts-2603`
- Input: `{"input": "text", "model": "...", "voice_id": "...", "stream": true, "response_format": "pcm"}`
- Output formats: `pcm`, `wav`, `mp3`, `flac`, `opus`
- Streaming: SSE with `speech.audio.delta` (base64 chunks) → `speech.audio.done`
- Custom voices: `POST /v1/audio/voices` with sample audio

### Agents API (beta) — `POST /v1/conversations`

- Create persistent agents with pre-configured tools + system prompt
- Server-side conversation state (no resend of history)
- Supported models: `mistral-medium-latest`, `mistral-large-latest`
- Built-in tools: web search, code interpreter, document library (RAG)
- Agent handoffs supported

## Healthcare Use Cases

### Synapse Medicine
- Mistral integrated into medical prescription decision support
- Deployed to **30,000 doctors in France**

### Santé publique France
- Generative AI experiment for epidemiological surveillance

## Compliance & Sovereignty

- European player, GDPR native
- On-prem deployment option for sensitive institutions
- Strong argument for V.I.T.A.L in Alan context

---
**Status:** Ingested + API reference added
**Confidence:** High
