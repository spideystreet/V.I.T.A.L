---
title: ElevenLabs
created: 2026-04-10
updated: 2026-04-10
type: entity
tags: [partner, api-reference, tts, voice]
sources:
  - elevenlabs.io/docs
---

# ElevenLabs

## Overview

Industry-leading TTS. Creator Tier free for hackathon (~100K chars/month). Best-in-class voice naturalness. French support.

## API Reference

### Base
- **URL:** `https://api.elevenlabs.io`
- **Auth:** `xi-api-key: <ELEVENLABS_API_KEY>`

### TTS Streaming — `POST /v1/text-to-speech/{voice_id}/stream`

```json
{
  "text": "Bonjour, comment vous sentez-vous ?",
  "model_id": "eleven_flash_v2_5",
  "output_format": "pcm_24000",
  "optimize_streaming_latency": 3
}
```

Response: chunked audio stream.

### Models

| Model | ID | Latency | Languages | Best for |
|-------|---|---------|-----------|----------|
| **Flash v2.5** | `eleven_flash_v2_5` | ~75ms | 32 (incl. FR) | Low-latency streaming |
| Eleven v3 | `eleven_v3` | moderate | 70+ | Best quality |
| Multilingual v2 | `eleven_multilingual_v2` | higher | 29 (FR + CA) | Multilingual |

### Output Formats
28 formats: PCM (8-48 kHz), MP3, WAV, Opus, alaw, ulaw.
Use `pcm_24000` to match current Voxtral pipeline.

### `optimize_streaming_latency` (0-4)
0 = max quality, 4 = min latency. Recommend 3 for demo.

## V.I.T.A.L Integration

**Swap in `voxtral.py`:** Replace `_stream_tts_to_queue()` with ElevenLabs endpoint. Same streaming pattern (HTTP chunked → audio queue). PCM format matches existing playback code.

**Fallback:** If ElevenLabs fails, revert to Voxtral TTS (one config toggle).

### vs Voxtral TTS

| | Voxtral | ElevenLabs Flash v2.5 |
|---|---|---|
| Latency (first byte) | ~200-400ms | ~75ms |
| Voice quality | Good | Best-in-class |
| French | Native | Supported |
| Integration | Already done | ~1h swap |
| Vendor alignment | Mistral ecosystem | Separate |

**Recommendation:** Use ElevenLabs for TTS (better voice, lower latency), keep Voxtral for STT.

## STT (Scribe v2)
ElevenLabs also has STT — 90+ languages, ~150ms latency. Not needed since Voxtral STT works fine.

---
**Status:** Ingested
**Confidence:** High
