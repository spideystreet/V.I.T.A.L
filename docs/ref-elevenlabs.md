# ElevenLabs TTS API — Dev Reference

> Compiled for V.I.T.A.L hackathon evaluation.
> Focus: Flash v2.5 streaming TTS as alternative/upgrade to Voxtral TTS.

---

## Authentication

All requests require the `xi-api-key` header.

```
xi-api-key: your_api_key_here
```

Base URLs (pick closest region):
- `https://api.elevenlabs.io` (default)
- `https://api.us.elevenlabs.io` (US)
- `https://api.eu.residency.elevenlabs.io` (EU — GDPR residency)
- `https://api.in.residency.elevenlabs.io` (India)

---

## Text-to-Speech (non-streaming)

**`POST /v1/text-to-speech/{voice_id}`**

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `voice_id` | string | Yes | Voice to use |

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output_format` | string | `mp3_44100_128` | Codec + sample rate + bitrate |
| `optimize_streaming_latency` | int (0-4) | null | Higher = faster, lower quality |
| `enable_logging` | bool | true | Set false for zero-retention (enterprise) |

### Request Body (JSON)

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `text` | string | -- | **Yes** | Text to convert to speech |
| `model_id` | string | `eleven_multilingual_v2` | No | Model to use |
| `language_code` | string | null | No | ISO 639-1 code to enforce language (e.g. `fr`, `en`) |
| `voice_settings` | object | null | No | Override voice characteristics (see below) |
| `seed` | int (0-4294967295) | null | No | Deterministic output |
| `previous_text` | string | null | No | Context from prior generation |
| `next_text` | string | null | No | Context from next generation |
| `previous_request_ids` | array | null | No | Up to 3 prior request IDs for continuity |
| `apply_text_normalization` | string | `auto` | No | `auto`, `on`, or `off` |

### Voice Settings Object

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `stability` | float | 0.5 | Randomness between generations (0=variable, 1=stable) |
| `similarity_boost` | float | 0.75 | Adherence to original voice |
| `style` | float | 0.0 | Style exaggeration |
| `speed` | float | 1.0 | Speed multiplier |
| `use_speaker_boost` | bool | true | Boost similarity to original speaker |

### Response

- **200**: Binary audio data (`application/octet-stream`)
- **422**: Validation error (JSON)

---

## Streaming TTS

**`POST /v1/text-to-speech/{voice_id}/stream`**

Same request body and query parameters as the non-streaming endpoint.

### Response

Returns `text/event-stream` — binary audio chunks streamed as they are generated.

### Python Example (SDK)

```python
from elevenlabs import ElevenLabs

client = ElevenLabs(api_key="xi-api-key")

audio_stream = client.text_to_speech.stream(
    voice_id="JBFqnCBsd6RMkjVDRZzb",
    text="How are you feeling today?",
    model_id="eleven_flash_v2_5",
    output_format="pcm_24000",
)

for chunk in audio_stream:
    # chunk is raw audio bytes — write to speaker or buffer
    play(chunk)
```

### Python Example (raw httpx, matches V.I.T.A.L patterns)

```python
import httpx

ELEVENLABS_API_KEY = os.environ["ELEVENLABS_API_KEY"]
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"

url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"
headers = {
    "xi-api-key": ELEVENLABS_API_KEY,
    "Content-Type": "application/json",
}
body = {
    "text": "How are you feeling today?",
    "model_id": "eleven_flash_v2_5",
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.75,
        "style": 0.0,
        "speed": 1.0,
    },
}

with httpx.Client() as client:
    with client.stream(
        "POST",
        url,
        headers=headers,
        json=body,
        params={"output_format": "pcm_24000"},
    ) as resp:
        resp.raise_for_status()
        for chunk in resp.iter_bytes(chunk_size=4096):
            # chunk is raw PCM bytes — push to audio queue
            audio_q.put(chunk)
```

> **Key difference from Voxtral**: ElevenLabs streams raw binary chunks directly (no SSE wrapper, no base64 encoding). Voxtral uses SSE with base64-encoded `audio_data` fields. The ElevenLabs approach is simpler and avoids the decode overhead.

---

## Output Formats

| Format | Value | Notes |
|--------|-------|-------|
| MP3 44.1kHz 128kbps | `mp3_44100_128` | Default, good balance |
| MP3 24kHz 48kbps | `mp3_24000_48` | Smaller, lower quality |
| PCM 24kHz | `pcm_24000` | Raw PCM, low latency |
| PCM 44.1kHz | `pcm_44100` | Raw PCM, high quality (Pro tier) |
| PCM 16kHz | `pcm_16000` | Telephony grade |
| Opus 48kHz | `opus_48000_128` | Efficient codec |
| u-law 8kHz | `ulaw_8000` | Telephony |
| a-law 8kHz | `alaw_8000` | Telephony |

**For V.I.T.A.L**: Use `pcm_24000` for lowest latency streaming. Matches well with sounddevice output at 24kHz.

---

## Models

| Model | ID | Languages | Latency | Character Limit | Best For |
|-------|----|-----------|---------|-----------------|----------|
| **Flash v2.5** | `eleven_flash_v2_5` | 32 (incl. FR + EN) | ~75ms | 40,000 chars | **Real-time, interactive, agents** |
| Multilingual v2 | `eleven_multilingual_v2` | 29 (incl. FR + EN) | Higher | 10,000 chars | Long-form, professional |
| v3 | `eleven_v3` | 70+ | Higher | 5,000 chars | Expressive, dramatic |
| ~~Turbo v2.5~~ | `eleven_turbo_v2_5` | 32 | Higher than Flash | -- | **Deprecated** — use Flash v2.5 |
| ~~Turbo v2~~ | `eleven_turbo_v2` | EN only | Higher | -- | **Deprecated** |

### Flash v2.5 Details

- **Latency**: ~75ms (excludes network/app overhead)
- **Price**: 50% lower per character than standard models
- **Languages**: 32 including French (FR + CA) and English (US, UK, AU, CA)
- **Text normalization**: Disabled by default for speed. Set `apply_text_normalization: "on"` if you need phone numbers / dates read naturally (adds latency, enterprise only).
- **Concurrency**: 2x standard (e.g., Free=4, Starter=6, Pro=20)
- **Best fit for V.I.T.A.L**: Yes — real-time voice health assistant needs sub-100ms TTS.

---

## Voices

### Listing Voices

```
GET /v1/voices
Header: xi-api-key: your_key
```

Returns all available voices (pre-made, cloned, generated).

> Voice Library voices (community) are **not available via API on free tier**.

### Voice Types

| Type | Description |
|------|-------------|
| Pre-made | ElevenLabs built-in voices |
| Community | 10,000+ voices from Voice Library |
| Instant Clone | Clone from 30s audio sample |
| Professional Clone | Extended training, Creator plan+ |
| Generated | Created via text prompt (Voice Design) |

### Multilingual Support

Both Flash v2.5 and Multilingual v2 support:
- **French**: France (`fr`) and Canada (`fr-CA`)
- **English**: US, UK, Australia, Canada

Use `language_code` parameter to force a specific language when the voice is multilingual.

---

## Concurrency Limits by Plan

| Plan | Multilingual v2 | Flash v2.5 | STT |
|------|-----------------|------------|-----|
| Free | 2 | 4 | 8 |
| Starter | 3 | 6 | 12 |
| Creator | 5 | 10 | 20 |
| Pro | 10 | 20 | 40 |
| Scale | 15 | 30 | 60 |

---

## Comparison: ElevenLabs Flash v2.5 vs Voxtral TTS

| Dimension | ElevenLabs Flash v2.5 | Voxtral (Mistral) |
|-----------|-----------------------|-------------------|
| **Latency** | ~75ms (claimed) | ~200-400ms (observed) |
| **Streaming** | Raw binary chunks (no encoding overhead) | SSE + base64-encoded PCM |
| **Output formats** | 28 options (MP3, PCM, Opus, WAV, telephony) | PCM only (float32) |
| **Languages** | 32 (FR + EN included) | FR + EN |
| **Voice quality** | Industry-leading naturalness | Good, improving |
| **Voice cloning** | Yes (instant + professional) | No |
| **Voice variety** | 10,000+ community voices | Limited voice IDs |
| **Pricing** | Per-character (50% discount on Flash) | Included in Mistral API credits |
| **Integration effort** | New dependency, new API key | Already integrated in V.I.T.A.L |
| **GDPR** | EU residency endpoint available | Mistral is EU-based |
| **SDK** | `elevenlabs` Python package | `mistralai` (already used) |

### V.I.T.A.L Integration Notes

1. **Drop-in replacement**: The `_stream_tts_to_queue()` function in `voxtral.py` would need changes — ElevenLabs streams raw bytes (no SSE parsing, no base64 decode), which simplifies the code.
2. **Sample rate**: Current V.I.T.A.L uses `TTS_SAMPLE_RATE` from config. ElevenLabs PCM outputs at the rate specified in `output_format` (e.g., `pcm_24000` = 24kHz). Match this to `sounddevice` output config.
3. **Prewarm**: The existing `prewarm_tts()` pattern (TLS connection warmup) applies — just change the target host to `api.elevenlabs.io`.
4. **Sentence buffering**: The existing `_buffer_sentences()` and clause-boundary detection logic works unchanged — just swap the TTS backend call.

---

## Quick Start Checklist

- [ ] Get API key from [elevenlabs.io/app/settings/api-keys](https://elevenlabs.io/app/settings/api-keys)
- [ ] Add `ELEVENLABS_API_KEY` to `.env`
- [ ] Pick a voice: browse at [elevenlabs.io/app/voice-library](https://elevenlabs.io/app/voice-library) or call `GET /v1/voices`
- [ ] Use model `eleven_flash_v2_5` for lowest latency
- [ ] Use `output_format=pcm_24000` for streaming to speakers
- [ ] Set `language_code=fr` for French sessions
- [ ] Install SDK: `pip install elevenlabs` (or use raw httpx as shown above)
