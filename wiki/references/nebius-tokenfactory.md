# Nebius Token Factory -- Developer Reference

> Comprehensive reference for the Nebius Token Factory API.
> Last fetched: 2026-04-10 from docs.tokenfactory.nebius.com

---

## 1. Overview

Nebius Token Factory is an inference-and-fine-tuning platform for open-source LLMs. It exposes an **OpenAI-compatible API** -- you can use the official OpenAI Python/JS SDK with a `base_url` override.

- **Console**: https://tokenfactory.nebius.com
- **API base URL**: `https://api.tokenfactory.nebius.com/v1/`
- **EU endpoint** (alternative): `https://api.tokenfactory.eu-west1.nebius.com/v1/`
- **OpenAPI spec**: https://api.tokenfactory.nebius.com/openapi.json
- **Cookbook**: https://github.com/nebius/token-factory-cookbook
- **Discord**: https://discord.com/invite/WJ2DUQRz4m

---

## 2. Authentication

```
Authorization: Bearer <NEBIUS_API_KEY>
```

### Get an API key

1. Go to https://tokenfactory.nebius.com, sign up with Google or GitHub
2. Navigate to **API keys** section: https://tokenfactory.nebius.com/project/api-keys
3. Click **Create API key**, name it, save it immediately (cannot be viewed again)
4. Export as env var: `export NEBIUS_API_KEY="your-key-here"`

### Trial credit

On first signup you get **$1 in trial credit**, valid for **30 days**.

### Promo code redemption

1. Click your **balance** in the nav menu
2. Click **Top up**
3. Select **With promo code**
4. Enter the promo code, click **Top up**
5. Balance increases immediately; verify in **Transactions** section

Note: Promo codes have expiration dates and **cannot** settle outstanding invoices.

---

## 3. OpenAI SDK Compatibility Setup

### Python

```python
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY"),
)
```

### JavaScript / Node.js

```javascript
const OpenAI = require("openai");

const client = new OpenAI({
    baseURL: "https://api.tokenfactory.nebius.com/v1/",
    apiKey: process.env.NEBIUS_API_KEY,
});
```

### cURL

```bash
curl 'https://api.tokenfactory.nebius.com/v1/chat/completions' \
  -X POST \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $NEBIUS_API_KEY" \
  --data-binary '{...}'
```

---

## 4. API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chat/completions` | POST | Chat completion (main endpoint) |
| `/v1/completions` | POST | Text completion (legacy/prompt-based) |
| `/v1/embeddings` | POST | Create embeddings |
| `/v1/rerank` | POST | Rerank documents by relevance |
| `/v1/responses` | POST | Responses API (OpenAI Responses format) |
| `/v1/models` | GET | List available models |
| `/v1/models?verbose=true` | GET | List models with pricing, context length, rate limits |
| `/v1/images/generations` | POST | Image generation |
| `/v1/files` | GET/POST/DELETE | File management |
| `/v1/fine_tuning/jobs` | GET/POST | Fine-tuning jobs |

All endpoints accept an optional `?ai_project_id=<string>` query param.

---

## 5. Chat Completion -- Full Request Schema

**POST** `/v1/chat/completions`

```json
{
  "model": "meta-llama/Llama-3.3-70B-Instruct",   // required
  "messages": [                                      // required, min 1
    {"role": "system", "content": "..."},
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    {"role": "tool", "content": "...", "tool_call_id": "...", "name": "..."}
  ],
  "max_tokens": 100,                    // int >= 0, optional
  "max_completion_tokens": 100,         // int >= 0, optional (incl. reasoning tokens)
  "temperature": 1.0,                   // 0.0-2.0, default 1
  "top_p": 1.0,                         // 0.0-1.0, default 1
  "top_k": 50,                          // optional (vLLM param)
  "n": 1,                               // 1-128, default 1
  "stream": false,                      // default false
  "stream_options": {"include_usage": true},  // optional
  "stop": ["<stop_seq>"],               // up to 4 sequences
  "presence_penalty": 0,                // -2.0 to 2.0
  "frequency_penalty": 0,              // -2.0 to 2.0
  "logit_bias": {"50256": -100},        // optional
  "logprobs": false,                    // default false
  "top_logprobs": null,                 // int >= 0 (requires logprobs=true)
  "tools": [...],                       // optional, see Function Calling
  "tool_choice": "auto",               // "none" | "auto" | "required" | {type, function}
  "reasoning_effort": "medium",        // "low" | "medium" | "high" (for reasoning models)
  "response_format": {"type": "json_object"},  // or {"type": "json_schema", "json_schema": {...}}
  "service_tier": "auto",              // "auto" | "flex"
  "user": "user-123",                  // optional end-user ID
  "store": false,                      // optional, model distillation
  "extra_body": {                      // optional vLLM params
    "guided_json": {"type": "object", "properties": {...}}
  }
}
```

### Response format

```json
{
  "id": "cmpl-bd18c4194f544c189578cfcb273a2f74",
  "object": "chat.completion",
  "created": 1717516032,
  "model": "meta-llama/Llama-3.3-70B-Instruct",
  "choices": [
    {
      "index": 0,
      "finish_reason": "stop",
      "message": {
        "role": "assistant",
        "content": "Hello!",
        "tool_calls": []
      },
      "logprobs": null
    }
  ],
  "usage": {
    "prompt_tokens": 13,
    "completion_tokens": 26,
    "total_tokens": 39
  }
}
```

---

## 6. Embeddings -- Full Request Schema

**POST** `/v1/embeddings`

```json
{
  "model": "BAAI/bge-en-icl",            // required
  "input": "text to embed",              // string | string[] | int[] | int[][]
  "encoding_format": "float",            // "float" | "base64", default "float"
  "dimensions": 4096,                    // optional (4096, 8192, etc.)
  "service_tier": "auto",               // "auto" | "flex"
  "user": "user-123"                     // optional
}
```

### Response

```json
{
  "object": "list",
  "data": [
    {
      "object": "embedding",
      "embedding": [0.0023064255, -0.009327292, ...],
      "index": 0
    }
  ],
  "model": "BAAI/bge-en-icl",
  "usage": {
    "prompt_tokens": 8,
    "total_tokens": 8
  }
}
```

---

## 7. Rerank -- Full Request Schema

**POST** `/v1/rerank`

```json
{
  "model": "Qwen/Qwen3-Reranker-8B",     // required
  "query": "What is the capital of France?",  // required
  "documents": ["Paris", "London", "Berlin"], // required, string[]
  "service_tier": "auto",
  "user": "user-123"
}
```

### Response

```json
{
  "id": "rerank-bbbxyuxyu643b6af",
  "model": "Qwen/Qwen3-Reranker-8B",
  "usage": {"prompt_tokens": 65, "total_tokens": 65},
  "results": [
    {"index": 1, "document": {"text": "Paris"}, "relevance_score": 0.9456},
    {"index": 0, "document": {"text": "London"}, "relevance_score": 0.1631}
  ]
}
```

---

## 8. Function Calling / Tool Use

### Supported `tool_choice` values

- `"auto"` -- model decides (default)
- `"none"` -- never call tools
- `"required"` -- must call a tool
- `{"type": "function", "function": {"name": "fn_name"}}` -- force specific function

### Tool definition format

```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to find the weather for"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["city", "unit"]
        }
    }
}]
```

### Full Python example

```python
import json, os
from openai import OpenAI

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.getenv("NEBIUS_API_KEY")
)

tools = [{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string"},
                "state": {"type": "string"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city", "state", "unit"]
        }
    }
}]

messages = [
    {"role": "user", "content": "What's the weather in Dallas, Fahrenheit?"}
]

# Step 1: model proposes tool call
response = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-fast",
    messages=messages,
    tools=tools,
    tool_choice="auto"
)

tool_calls = response.choices[0].message.tool_calls
messages.append({"role": "assistant", "tool_calls": tool_calls})

# Step 2: execute tool and return result
for call in tool_calls:
    args = json.loads(call.function.arguments)
    result = get_current_weather(**args)  # your function
    messages.append({
        "role": "tool",
        "content": result,
        "tool_call_id": call.id,
        "name": call.function.name
    })

# Step 3: model generates final response
final = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-fast",
    messages=messages,
    tools=tools
)
```

### Tool call response format

```json
{
  "choices": [{
    "message": {
      "role": "assistant",
      "tool_calls": [{
        "id": "chatcmpl-tool-99a7259c139e4aa986549d07cde8df8f",
        "type": "function",
        "function": {
          "name": "get_current_weather",
          "arguments": "{\"city\": \"Dallas\", \"state\": \"Texas\", \"unit\": \"fahrenheit\"}"
        }
      }]
    }
  }]
}
```

---

## 9. Structured Output / JSON Mode

### Option A: json_object (arbitrary JSON)

```python
response = client.chat.completions.create(
    model="Qwen/Qwen3-235B-A22B",
    messages=[...],
    response_format={"type": "json_object"}
)
```

### Option B: json_schema (strict schema)

```python
from pydantic import BaseModel
from typing import List, Literal

class Film(BaseModel):
    title: str
    year: int
    director: str
    cast: List[str]
    genre: Literal["drama", "thriller", "sci-fi", "comedy", "horror", "fantasy"]

response = client.chat.completions.create(
    model="Qwen/Qwen3-235B-A22B",
    response_format={
        "type": "json_schema",
        "json_schema": Film.model_json_schema()
    },
    messages=[...]
)
```

### Option C: guided_json via extra_body (vLLM native)

```python
response = client.chat.completions.create(
    model="...",
    messages=[...],
    extra_body={
        "guided_json": {
            "type": "object",
            "properties": {
                "score": {"type": "number"},
                "reason": {"type": "string"}
            },
            "required": ["score", "reason"]
        }
    }
)
```

---

## 10. Available Models -- Hackathon Relevant

### Pricing format

Pricing from the verbose `/v1/models?verbose=true` endpoint returns per-token costs:
- `pricing.prompt` = cost per 1 input token
- `pricing.completion` = cost per 1 output token

To get per-1M-token cost: multiply by 1,000,000.

### Model flavors

- **Base** (default): higher throughput, lower cost
- **Fast** (append `-fast` to model ID): lower latency, speculative decoding, higher cost

### Key models for health AI hackathon

| Model ID | Type | Context | Notes |
|----------|------|---------|-------|
| **Guardrails** | | | |
| `meta-llama/Llama-Guard-3-8B` | Safety | 8K | Content safety classification, input/output guardrails |
| **LLMs (text-to-text)** | | | |
| `meta-llama/Llama-3.3-70B-Instruct` | Chat | 128K | Strong general-purpose, function calling support |
| `meta-llama/Meta-Llama-3.1-8B-Instruct-fast` | Chat | 128K | Fast, cheap, good for tool routing |
| `meta-llama/Meta-Llama-3.1-70B-Instruct` | Chat | 128K | Predecessor, still solid |
| `Qwen/Qwen3-235B-A22B` | Chat/MoE | 128K+ | Massive MoE, strong structured output |
| `Qwen/Qwen3-30B-A3B` | Chat/MoE | 128K+ | Smaller MoE, cost-effective |
| **Reasoning** | | | |
| `deepseek-ai/DeepSeek-R1-0528` | Reasoning | 128K | Deep reasoning with `reasoning_effort` param |
| `deepseek-ai/DeepSeek-V3-0324` | Chat | 128K | Fast general-purpose |
| `Qwen/QwQ-32B` | Reasoning | 128K | Reasoning model |
| **Embeddings** | | | |
| `BAAI/bge-en-icl` | Embedding | - | English, 1536-dim default |
| `BAAI/bge-multilingual-gemma2` | Embedding | - | Multilingual (FR/EN), Gemma2-based |
| `intfloat/e5-mistral-7b-instruct` | Embedding | - | Mistral-based, instruction-tuned |
| **Reranking** | | | |
| `Qwen/Qwen3-Reranker-8B` | Rerank | - | Document reranking |
| **Vision** | | | |
| `Qwen/Qwen2.5-VL-72B-Instruct` | Vision | 128K | Image understanding |
| **Code** | | | |
| `Qwen/Qwen2.5-Coder-32B-Instruct` | Code | 128K | Code generation |
| **Other notable** | | | |
| `moonshotai/Kimi-K2.5` | Chat | 128K+ | Recent model |
| `mistralai/Mistral-Nemo-Instruct-2407` | Chat | 128K | Mistral Nemo |

### Pricing examples (from verbose API, per-token)

From the verbose model list, example for `Meta-Llama-3.1-8B-Instruct-fast`:
- `prompt`: $0.00000003/token = **$0.03 / 1M input tokens**
- `completion`: $0.00000009/token = **$0.09 / 1M output tokens**

For exact current pricing on all models, query:
```bash
curl -s 'https://api.tokenfactory.nebius.com/v1/models?verbose=true' \
  -H "Authorization: Bearer $NEBIUS_API_KEY" | \
  jq '.data[] | {id, pricing, context_length, per_request_limits}'
```

---

## 11. Rate Limits & Scaling

### Default limits (Startup Tier)

Visible at: https://tokenfactory.nebius.com/project/rate-limits

Example baseline (from docs):
- **RPM** (requests/min): 60
- **TPM** (tokens/min): 400,000

### Dynamic auto-scaling

Limits are evaluated in **rolling 15-minute windows**:

| Condition | Action |
|-----------|--------|
| Avg usage >= 80% of limit | Next window: limit x 1.2 (scale up) |
| Avg usage <= 50% of limit | Next window: limit / 1.5 (scale down) |
| Hard ceiling | 20x base allocation (then need Enterprise) |

### Scale-up progression (sustained >= 80%)

| Window | Scale | RPM | TPM |
|--------|-------|-----|-----|
| Baseline | 1.00x | 60 | 400,000 |
| +15 min | 1.20x | 72 | 480,000 |
| +30 min | 1.44x | 86 | 576,000 |
| +1 h | 2.07x | 124 | 828,000 |
| +2 h | 4.30x | 258 | 1,720,000 |

### Rate limit headers

| Header | Description |
|--------|-------------|
| `x-ratelimit-limit-requests` | Max RPM |
| `x-ratelimit-limit-tokens` | Max TPM |
| `x-ratelimit-remaining-requests` | Remaining RPM |
| `x-ratelimit-remaining-tokens` | Remaining TPM |
| `x-ratelimit-reset-requests` | Seconds until RPM reset |
| `x-ratelimit-reset-tokens` | Seconds until TPM reset |
| `x-ratelimit-dynamic-scale-requests` | Current dynamic scale factor (requests) |
| `x-ratelimit-dynamic-scale-tokens` | Current dynamic scale factor (tokens) |
| `x-ratelimit-dynamic-period-remaining` | Seconds until next adjustment |
| `x-ratelimit-over-limit` | "yes" if processed despite being over limit |
| `Retry-After` | Seconds to wait on 429 |

### Over-limit processing

Requests over limit may still be processed at lower priority if spare capacity exists. Response includes `x-ratelimit-over-limit: yes`.

### Batch API

Async/batch inference has **significantly higher base limits** and **50% price discount**. Use for bulk/async workloads.

---

## 12. Billing & Payment

### Payment methods

| Method | Type | Details |
|--------|------|---------|
| Bank card | Individual/Company | Real-time debit, auto-charge on negative balance or threshold |
| Bank transfer | Company only | Manual top-up via proforma invoice |

### Auto-charging triggers (bank card)

1. Start of month if balance is negative
2. When billing threshold is reached

### Trial credit

- **$1** on signup, valid **30 days**

### Promo codes

- Applied via Top up > With promo code
- Have expiration dates
- Cannot settle outstanding invoices
- Balance increases immediately

### Taxes

- Netherlands: 21% VAT
- Other EU (company): no VAT
- Other EU (individual): country-specific VAT
- US: Texas and Washington only
- Rest of world (company): no tax

---

## 13. HIPAA Compliance

Nebius Token Factory supports **HIPAA/BAA** for healthcare use cases:

### Covered under BAA

| Feature | Covered? | Requirements |
|---------|----------|-------------|
| `/chat/completions` | Yes | Must enable Zero Data Retention |
| `/completions` | Yes | Must enable Zero Data Retention |
| Fine-tuning | No | Excluded |
| Batch inference | No | Excluded |
| Embeddings, files, datasets | No | Not covered |

### Requirements

1. Sign a BAA with Nebius before transmitting PHI/ePHI
2. Use only covered API methods
3. Enable Zero Data Retention
4. Do not include ePHI/PII in metadata, tags, or key names

### How to get BAA

1. Contact account manager
2. Provide intended use case
3. Confirm covered methods + zero data retention
4. Sign BAA document

---

## 14. Model Flavors & Inference Optimizations

### Two flavors

| Flavor | Suffix | Characteristics |
|--------|--------|----------------|
| Base | (none) | Higher throughput, lower cost |
| Fast | `-fast` | Lower latency, speculative decoding, higher cost |

Both produce identical outputs. To use fast: `meta-llama/Meta-Llama-3.1-8B-Instruct-fast`

### Inference optimizations applied

- KV Cache
- Paged Attention
- Flash Attention
- Quantization (fp8)
- Continuous Batching
- Context Caching
- Speculative Decoding (fast flavor)

Quality impact: ~99% of original model quality maintained.

### GPU types used

L40, H100, H200, B200

---

## 15. List Models Programmatically

### Python

```python
models = client.models.list()
for m in models.data:
    print(m.id)
```

### Verbose (with pricing + limits)

```bash
curl -s 'https://api.tokenfactory.nebius.com/v1/models?verbose=true' \
  -H "Authorization: Bearer $NEBIUS_API_KEY" | \
  jq '.data[] | select(.id | test("llama|guard|bge|e5|deepseek|qwen"; "i")) | {id, context_length, pricing, per_request_limits}'
```

### Verbose response structure

```json
{
  "id": "meta-llama/Meta-Llama-3.1-8B-Instruct-fast",
  "name": "Meta-Llama-3.1-8B-Instruct (fast)",
  "created": 1750954196,
  "description": "",
  "context_length": 131072,
  "architecture": {
    "modality": "text->text",
    "tokenizer": "Other"
  },
  "quantization": "fp8",
  "pricing": {
    "prompt": "0.00000003",
    "completion": "0.00000009",
    "image": "0",
    "price_per_video_second": "0",
    "request": "0"
  },
  "per_request_limits": {
    "tokens_per_minute": 800000.0,
    "requests_per_minute": 1200.0,
    "burst_ratio": 1.0
  },
  "object": "model",
  "owned_by": "system"
}
```

---

## 16. Quick Recipes for Hackathon

### Health checkup with Llama 3.3 70B + function calling

```python
import os, json
from openai import OpenAI

client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY"),
)

tools = [{
    "type": "function",
    "function": {
        "name": "get_health_summary",
        "description": "Get aggregated health metrics over a time window",
        "parameters": {
            "type": "object",
            "properties": {
                "hours": {"type": "integer", "description": "Time window in hours"}
            },
            "required": ["hours"]
        }
    }
}]

response = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct",
    messages=[
        {"role": "system", "content": "You are a health assistant."},
        {"role": "user", "content": "How have my vitals been in the last 24 hours?"}
    ],
    tools=tools,
    tool_choice="auto",
    temperature=0.6
)
```

### Safety guardrail with Llama Guard

```python
guard_response = client.chat.completions.create(
    model="meta-llama/Llama-Guard-3-8B",
    messages=[
        {"role": "user", "content": user_input}
    ],
    max_tokens=100
)
# Check if response indicates unsafe content
safety_result = guard_response.choices[0].message.content
is_safe = "safe" in safety_result.lower()
```

### Embeddings for health context retrieval

```python
embedding = client.embeddings.create(
    model="BAAI/bge-multilingual-gemma2",
    input="heart rate variability stress patterns",
    encoding_format="float"
)
vector = embedding.data[0].embedding
```

### Streaming chat completion

```python
stream = client.chat.completions.create(
    model="meta-llama/Llama-3.3-70B-Instruct",
    messages=[{"role": "user", "content": "Analyze my sleep quality"}],
    stream=True,
    stream_options={"include_usage": True}
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

---

## 17. Key Links

| Resource | URL |
|----------|-----|
| Console | https://tokenfactory.nebius.com |
| API keys | https://tokenfactory.nebius.com/project/api-keys |
| Rate limits dashboard | https://tokenfactory.nebius.com/project/rate-limits |
| Playground | https://tokenfactory.nebius.com/playground |
| OpenAPI spec | https://api.tokenfactory.nebius.com/openapi.json |
| Docs home | https://docs.tokenfactory.nebius.com |
| llms.txt (full index) | https://docs.tokenfactory.nebius.com/llms.txt |
| Cookbook (GitHub) | https://github.com/nebius/token-factory-cookbook |
| Function calling cookbook | https://github.com/nebius/token-factory-cookbook/tree/main/tool-calling |
| Integrations | https://docs.tokenfactory.nebius.com/integrations/overview |
| Fine-tuning guide | https://docs.tokenfactory.nebius.com/post-training/how-to-fine-tune |
| HIPAA guide | https://docs.tokenfactory.nebius.com/legal/hipaa-guideline |
| Discord | https://discord.com/invite/WJ2DUQRz4m |
