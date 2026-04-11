# Mistral AI API — Dev Reference

> Compiled for V.I.T.A.L hackathon. Focused on endpoints, schemas, and code.

**Base URL:** `https://api.mistral.ai`

---

## Authentication

All requests require a Bearer token in the `Authorization` header:

```
Authorization: Bearer $MISTRAL_API_KEY
```

Get your key at [console.mistral.ai](https://console.mistral.ai) → Organization settings → API keys.

---

## Models

| Model | API ID | Context | Input $/M | Output $/M | Notes |
|-------|--------|---------|-----------|------------|-------|
| Mistral Large 3 | `mistral-large-3` | 128k | Custom | Custom | Multimodal, vision, chat |
| Mistral Medium 3.1 | `mistral-medium-3108` | 128k | Custom | Custom | Frontier-class, multimodal |
| **Mistral Small 4** | `mistral-small-4` | 32k | Custom | Custom | Instruct, reasoning, coding — **used by V.I.T.A.L** |
| Mistral Small 3.2 | `mistral-small-2506` | 32k | $0.1 | $0.3 | General-purpose |
| Ministral 3 14B | `ministral-3-14b` | 128k | Custom | Custom | Text + vision |
| Ministral 3 8B | `ministral-3-8b` | 128k | Custom | Custom | Efficient, multimodal |
| Ministral 3 3B | `ministral-3-3b` | 128k | Custom | Custom | Tiny, efficient |
| Devstral 2 | `devstral-2-25-12` | 256k | $0.1 | $0.3 | Code agents, tooling |
| Codestral | `codestral-2508` | 256k | Custom | Custom | Code completion, frontier |
| Magistral Medium 1.2 | `magistral-medium-2509` | 40k | $2 | $5 | Reasoning, multimodal |
| Magistral Small 1.2 | `magistral-small-2509` | 40k | Custom | Custom | Reasoning, small |
| **Voxtral TTS** | `voxtral-mini-tts-2603` | — | Custom | Custom | Text-to-speech, voice cloning — **used by V.I.T.A.L** |
| **Voxtral Transcribe 2** | `voxtral-mini-latest` | — | Custom | Custom | STT, diarization, 13 languages — **used by V.I.T.A.L** |
| OCR 3 | `mistral-ocr-3` | — | Custom | Custom | Document processing |

All models support: chat completions, function calling, structured outputs, batching.

---

## Chat Completions

### Endpoint

```
POST /v1/chat/completions
```

### Request Schema

```json
{
  "model": "mistral-small-4",
  "messages": [
    {"role": "system", "content": "You are a health assistant."},
    {"role": "user", "content": "How am I doing?"}
  ],
  "temperature": 0.3,
  "top_p": 1,
  "max_tokens": 1024,
  "stream": false,
  "stop": ["\n\n"],
  "random_seed": null,
  "safe_prompt": false,
  "response_format": {"type": "text"},
  "tools": [],
  "tool_choice": "auto",
  "parallel_tool_calls": true,
  "frequency_penalty": 0,
  "presence_penalty": 0
}
```

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `model` | string | required | Model ID |
| `messages` | array | required | `system`, `user`, `assistant`, `tool` roles |
| `temperature` | float | model-dependent | 0.0–0.7 recommended |
| `top_p` | float | 1 | Nucleus sampling |
| `max_tokens` | int | null | Max output tokens |
| `stream` | bool | false | SSE streaming |
| `stop` | string/array | — | Stop sequences |
| `random_seed` | int | null | Deterministic output |
| `safe_prompt` | bool | false | Inject safety prompt |
| `response_format` | object | `{"type":"text"}` | `text`, `json_object`, `json_schema` |
| `tools` | array | — | Tool definitions (see Function Calling) |
| `tool_choice` | string | `"auto"` | `auto`, `any`, `none` |
| `parallel_tool_calls` | bool | true | Allow parallel tool use |
| `frequency_penalty` | float | 0 | Penalize repeated tokens |
| `presence_penalty` | float | 0 | Penalize repeated topics |
| `reasoning_effort` | string | — | `"high"`, `"none"` |

### Response Schema

```json
{
  "id": "cmpl-abc123",
  "object": "chat.completion",
  "created": 1700000000,
  "model": "mistral-small-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Based on your data..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 42,
    "completion_tokens": 100,
    "total_tokens": 142
  }
}
```

### Streaming (SSE)

When `stream: true`, response is `text/event-stream`. Each event is a `CompletionEvent` with partial delta content. Stream terminates with `[DONE]`.

### Python Example (httpx)

```python
import httpx, os, json

resp = httpx.post(
    "https://api.mistral.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"},
    json={
        "model": "mistral-small-4",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 256,
    },
    timeout=30,
)
data = resp.json()
print(data["choices"][0]["message"]["content"])
```

#### Streaming with httpx

```python
import httpx, os, json

with httpx.stream(
    "POST",
    "https://api.mistral.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"},
    json={
        "model": "mistral-small-4",
        "messages": [{"role": "user", "content": "Hello"}],
        "stream": True,
    },
    timeout=60,
) as resp:
    for line in resp.iter_lines():
        if line.startswith("data: "):
            payload = line[6:]
            if payload.strip() == "[DONE]":
                break
            chunk = json.loads(payload)
            delta = chunk["choices"][0]["delta"].get("content", "")
            print(delta, end="", flush=True)
```

---

## Function Calling

### Tool Definition Schema

```json
{
  "type": "function",
  "function": {
    "name": "get_health_summary",
    "description": "Returns aggregated health metrics over a time window",
    "parameters": {
      "type": "object",
      "properties": {
        "hours": {
          "type": "integer",
          "description": "Number of hours to look back"
        }
      },
      "required": ["hours"]
    }
  }
}
```

### tool_choice Options

| Value | Behavior |
|-------|----------|
| `"auto"` | Model decides whether to call tools (default) |
| `"any"` | Model is forced to call at least one tool |
| `"none"` | Model will not call any tools |

### parallel_tool_calls

| Value | Behavior |
|-------|----------|
| `true` | Model may invoke multiple tools in one turn (default) |
| `false` | Enforces sequential, one-tool-at-a-time calling |

### How Tool Calls Come Back

When the model decides to call tools, the response `message` contains a `tool_calls` array:

```json
{
  "role": "assistant",
  "content": null,
  "tool_calls": [
    {
      "id": "call_abc123",
      "type": "function",
      "function": {
        "name": "get_health_summary",
        "arguments": "{\"hours\": 24}"
      }
    }
  ]
}
```

- `function.arguments` is a **JSON string** — parse it with `json.loads()`
- `id` must be echoed back in the tool result message
- `finish_reason` will be `"tool_calls"` (not `"stop"`)

### Sending Tool Results Back

Append the assistant message with `tool_calls`, then a `tool` message per call:

```json
{
  "role": "tool",
  "name": "get_health_summary",
  "content": "{\"heart_rate_avg\": 72, \"steps\": 8500}",
  "tool_call_id": "call_abc123"
}
```

Then call `/v1/chat/completions` again with the full message history. The model generates a natural language response using the tool results.

### Full Message Flow

```
system → user → assistant (tool_calls) → tool (result) → assistant (final answer)
```

Multiple tool calls can happen in sequence or parallel before the final answer.

### Python Example (httpx)

```python
import httpx, os, json

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_health_summary",
            "description": "Aggregated health metrics over a time window",
            "parameters": {
                "type": "object",
                "properties": {
                    "hours": {"type": "integer", "description": "Hours to look back"}
                },
                "required": ["hours"],
            },
        },
    }
]

messages = [
    {"role": "system", "content": "You are a health assistant with tool access."},
    {"role": "user", "content": "How was my sleep last night?"},
]

# Step 1: Initial call
resp = httpx.post(
    "https://api.mistral.ai/v1/chat/completions",
    headers={"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"},
    json={"model": "mistral-small-4", "messages": messages, "tools": tools},
    timeout=30,
)
msg = resp.json()["choices"][0]["message"]

if msg.get("tool_calls"):
    messages.append(msg)  # Append assistant message with tool_calls

    for tc in msg["tool_calls"]:
        name = tc["function"]["name"]
        args = json.loads(tc["function"]["arguments"])

        # Step 2: Execute tool locally
        result = execute_tool(name, args)  # Your implementation

        messages.append({
            "role": "tool",
            "name": name,
            "content": json.dumps(result),
            "tool_call_id": tc["id"],
        })

    # Step 3: Get final answer
    resp2 = httpx.post(
        "https://api.mistral.ai/v1/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"},
        json={"model": "mistral-small-4", "messages": messages, "tools": tools},
        timeout=30,
    )
    final = resp2.json()["choices"][0]["message"]["content"]
```

---

## STT — Voxtral Transcribe 2

### Endpoint

```
POST /v1/audio/transcriptions
```

### Model ID

`voxtral-mini-latest` (alias for Voxtral Mini Transcribe V2)

### Request Parameters

| Parameter | Type | Required | Default | Notes |
|-----------|------|----------|---------|-------|
| `model` | string | yes | — | `"voxtral-mini-latest"` |
| `file` | File | no* | — | Binary audio upload |
| `file_id` | string | no* | — | ID from `/v1/files` upload |
| `file_url` | string | no* | — | URL of audio to transcribe |
| `language` | string | no | auto | ISO code, e.g. `"en"`, `"fr"` |
| `temperature` | float | no | — | Sampling temperature |
| `diarize` | bool | no | false | Speaker diarization |
| `context_bias` | array | no | — | Up to 100 terms for spelling guidance |
| `timestamp_granularities` | array | no | — | `["segment"]` and/or `["word"]` |
| `stream` | bool | no | false | SSE streaming |

*One of `file`, `file_id`, or `file_url` is required.

### Supported Audio Formats

MP3, WAV (and likely other common formats). Max duration: ~3 hours per request.

### Supported Languages (13)

English, Chinese, Hindi, Spanish, Arabic, French, Portuguese, Russian, German, Japanese, Korean, Italian, Dutch.

### Response Schema

```json
{
  "model": "voxtral-mini-latest",
  "text": "The transcribed text...",
  "language": "en",
  "segments": [
    {
      "text": "segment text",
      "start": 0.0,
      "end": 2.5
    }
  ],
  "usage": {
    "prompt_audio_seconds": 30,
    "prompt_tokens": 150,
    "completion_tokens": 42,
    "total_tokens": 192
  }
}
```

### Python Example (httpx)

```python
import httpx, os

with open("recording.mp3", "rb") as f:
    resp = httpx.post(
        "https://api.mistral.ai/v1/audio/transcriptions",
        headers={"Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}"},
        files={"file": ("recording.mp3", f, "audio/mpeg")},
        data={
            "model": "voxtral-mini-latest",
            "language": "en",
        },
        timeout=120,
    )

result = resp.json()
print(result["text"])
```

### Python Example (SDK)

```python
from mistralai.client import Mistral

client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])

with open("recording.mp3", "rb") as f:
    result = client.audio.transcriptions.complete(
        model="voxtral-mini-latest",
        file={"content": f, "file_name": "recording.mp3"},
    )
print(result.text)
```

---

## TTS — Voxtral TTS

### Endpoint

```
POST /v1/audio/speech
```

### Model ID

`voxtral-mini-tts-2603`

### Request Schema (JSON)

```json
{
  "model": "voxtral-mini-tts-2603",
  "input": "Hello, how are you feeling today?",
  "voice_id": "your-voice-id",
  "response_format": "mp3",
  "stream": false
}
```

| Parameter | Type | Required | Default | Notes |
|-----------|------|----------|---------|-------|
| `model` | string | yes | — | `"voxtral-mini-tts-2603"` |
| `input` | string | yes | — | Text to synthesize (max ~300 words) |
| `voice_id` | string | no* | — | Saved voice ID |
| `ref_audio` | string | no* | — | Base64-encoded audio for zero-shot cloning |
| `response_format` | string | no | — | `pcm`, `wav`, `mp3`, `flac`, `opus` |
| `stream` | bool | no | false | SSE streaming |

*One of `voice_id` or `ref_audio` is required for voice selection.

### Output Formats

| Format | Use Case | Latency |
|--------|----------|---------|
| `pcm` | Streaming playback (raw float32 LE) | ~0.8s TTFA |
| `wav` | Highest quality, uncompressed | — |
| `mp3` | General use, compressed | ~3s TTFA |
| `flac` | Lossless compression | — |
| `opus` | Low bitrate streaming | — |

TTFA = time-to-first-audio (end-to-end API latency). Processing latency is ~90ms.

### Response (non-streaming)

```json
{
  "audio_data": "<base64-encoded audio bytes>"
}
```

### Streaming Response (SSE)

When `stream: true`, returns `text/event-stream`:

- **`speech.audio.delta`** — contains `audio_data` field with base64-encoded audio fragment
- **`speech.audio.done`** — contains `usage` with token information

### Python Example (httpx)

```python
import httpx, os, base64
from pathlib import Path

resp = httpx.post(
    "https://api.mistral.ai/v1/audio/speech",
    headers={
        "Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "voxtral-mini-tts-2603",
        "input": "You slept 7 hours with good deep sleep phases.",
        "voice_id": "your-voice-id",
        "response_format": "mp3",
    },
    timeout=30,
)
audio_b64 = resp.json()["audio_data"]
Path("output.mp3").write_bytes(base64.b64decode(audio_b64))
```

#### Streaming TTS with httpx

```python
import httpx, os, json, base64

with httpx.stream(
    "POST",
    "https://api.mistral.ai/v1/audio/speech",
    headers={
        "Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "voxtral-mini-tts-2603",
        "input": "Your heart rate has been elevated today.",
        "voice_id": "your-voice-id",
        "response_format": "pcm",
        "stream": True,
    },
    timeout=60,
) as resp:
    for line in resp.iter_lines():
        if line.startswith("data: "):
            payload = json.loads(line[6:])
            event_type = payload.get("type")
            if event_type == "speech.audio.delta":
                chunk = base64.b64decode(payload["audio_data"])
                # Feed chunk to audio player
            elif event_type == "speech.audio.done":
                break
```

### Voice Management

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Create voice | POST | `/v1/audio/voices` |
| List voices | GET | `/v1/audio/voices` |
| Get voice | GET | `/v1/audio/voices/{voice_id}` |
| Update voice | PATCH | `/v1/audio/voices/{voice_id}` |
| Delete voice | DELETE | `/v1/audio/voices/{voice_id}` |
| Get sample audio | GET | `/v1/audio/voices/{voice_id}/sample` |

#### Create Voice

```python
import httpx, os, base64

with open("voice_sample.wav", "rb") as f:
    sample_b64 = base64.b64encode(f.read()).decode()

resp = httpx.post(
    "https://api.mistral.ai/v1/audio/voices",
    headers={
        "Authorization": f"Bearer {os.environ['MISTRAL_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "name": "vital-assistant",
        "sample_audio": sample_b64,
        "languages": ["en", "fr"],
    },
)
voice_id = resp.json()["id"]
```

Voice cloning works from as little as 2-3 seconds of reference audio. Supports: English, French, Spanish, Portuguese, Italian, Dutch, German, Hindi, Arabic.

---

## Rate Limits & Errors

### Common HTTP Error Codes

| Code | Meaning | Action |
|------|---------|--------|
| `400` | Bad request (invalid params) | Check request body |
| `401` | Unauthorized (bad/missing API key) | Check `Authorization` header |
| `403` | Forbidden (insufficient permissions) | Check API key scopes |
| `422` | Validation error (schema mismatch) | Check parameter types/values |
| `429` | Rate limited | Back off and retry with exponential delay |
| `500` | Internal server error | Retry after a short delay |

### Rate Limits

Rate limits are per-API-key and vary by model and plan tier. The API returns `429` when limits are exceeded. Use exponential backoff for retries.

### Retry Pattern (Python)

```python
import httpx, time

def call_with_retry(url, headers, json_body, max_retries=3):
    for attempt in range(max_retries):
        resp = httpx.post(url, headers=headers, json=json_body, timeout=30)
        if resp.status_code == 429:
            wait = 2 ** attempt
            time.sleep(wait)
            continue
        resp.raise_for_status()
        return resp.json()
    raise Exception("Max retries exceeded")
```

---

## Quick Reference

| What | Value |
|------|-------|
| Base URL | `https://api.mistral.ai` |
| Auth header | `Authorization: Bearer $MISTRAL_API_KEY` |
| Chat model (V.I.T.A.L) | `mistral-small-4` |
| STT model | `voxtral-mini-latest` |
| TTS model | `voxtral-mini-tts-2603` |
| Chat endpoint | `POST /v1/chat/completions` |
| STT endpoint | `POST /v1/audio/transcriptions` |
| TTS endpoint | `POST /v1/audio/speech` |
| Voice CRUD | `/v1/audio/voices` |
| OpenAPI spec | `https://api.mistral.ai/openapi.yaml` |
| Console | `https://console.mistral.ai` |
