---
title: Nebius TokenFactory
created: 2026-04-10
updated: 2026-04-10
type: entity
tags: [partner, api-reference, inference, open-source]
sources:
  - docs.tokenfactory.nebius.com
  - nebius.com/docs
---

# Nebius TokenFactory

## Overview

Managed inference API for 60+ open-source models. OpenAI-compatible format (drop-in replacement). Hackathon credits: $50.

## API Reference

### Base
- **URL:** `https://api.tokenfactory.nebius.com/v1/`
- **Auth:** `Authorization: Bearer <NEBIUS_API_KEY>`
- **Format:** OpenAI-compatible (`/chat/completions`, `/embeddings`)
- **SDK:** Standard OpenAI SDK with `base_url` override

### Usage with OpenAI SDK
```python
from openai import OpenAI
client = OpenAI(
    base_url="https://api.tokenfactory.nebius.com/v1/",
    api_key=NEBIUS_API_KEY
)
```

## Relevant Models

### LLMs
| Model | Cost (in/out per 1M tok) | Notes |
|-------|--------------------------|-------|
| Llama 3.3 70B Instruct | $0.13 / $0.40 | Best backup LLM |
| DeepSeek V3 | $0.50 / $1.50 | Strong reasoning |
| Qwen3 235B A22B | $0.20 / $0.80 | MoE, very capable |
| Devstral Small 2505 | $0.08 / $0.24 | Mistral coding model |

### Guardrails
| Model | Cost | Purpose |
|-------|------|---------|
| **Llama Guard 3 8B** | $0.20 / $0.60 | Content safety — block medical diagnosis |

### Embeddings
| Model | Cost | Purpose |
|-------|------|---------|
| bge-multilingual-gemma2 | $0.01 / 1M tok | Multilingual health data embeddings |
| e5-mistral-7b-instruct | $0.01 / 1M tok | Semantic search |

### No audio/voice models — cannot replace Voxtral or ElevenLabs

## Rate Limits
- Baseline: 60 RPM, 400K TPM
- Auto-scales to 20x (1,200 RPM / 8M TPM)
- Batch API: 50% discount

## V.I.T.A.L Use Cases (ranked)

1. **Guardrails (Llama Guard)** — validate LLM doesn't cross into medical diagnosis. ~30min integration. Great for judges.
2. **LLM fallback** — if Mistral API dies during demo, switch to Llama 70B. ~15min config change.
3. **Embeddings** — semantic search on health patterns. Nice-to-have.

## $50 Budget

| Model | $50 buys |
|-------|----------|
| Llama Guard (guardrails) | ~250M tokens — unlimited for hackathon |
| Llama 70B (fallback) | ~100M tokens — unlimited for hackathon |
| Embeddings | ~5B tokens — unlimited for hackathon |

---
**Status:** Ingested
**Confidence:** High
