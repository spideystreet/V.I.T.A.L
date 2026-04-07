# Voxtral TTS – Voice Pipeline (raw notes)

**Primary source**: https://arxiv.org/pdf/2603.25551
**Reading date**: 2026-04-07
**Status**: raw (do not modify)

---

## Context

- Neural TTS model developed as part of Mistral / Voxtral ecosystem
- arXiv paper 2603.25551: technical documentation, architecture, performance benchmarks
- **TTS choice for V.I.T.A.L: Voxtral TTS for agent voice response**

## Points to Extract from Paper

- Model architecture (encoder/decoder, sampling strategy)
- End-to-end audio generation latency
- Voice quality: naturalness, expressiveness, French language support
- Deployment modes: API, on-prem, edge, streaming chunks?
- Comparison vs ElevenLabs, Coqui, OpenAI TTS

## Relevance for V.I.T.A.L

- V.I.T.A.L is voice-first: TTS quality and latency are critical for UX
- Voxtral = 100% Mistral stack → consistency across LLM + TTS
- Native French support = essential for FR market (Alan)

## Unknown / To Confirm

- Is end-to-end latency compatible with real-time UX (< 500ms)?
- Is Voxtral TTS available via standard Mistral API today?
- Is there an audio streaming mode to reduce perceived latency?