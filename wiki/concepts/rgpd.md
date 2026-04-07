---
title: RGPD & Privacy
created: 2026-04-08
updated: 2026-04-08
type: concept
tags: [privacy, compliance, pitch]
sources:
  - mistral_health.md
  - healthkit.md
---

# RGPD & Privacy

## Why this matters for V.I.T.A.L

V.I.T.A.L processes **health data** (HRV, sleep, resting HR) and **voice recordings** — both classified as sensitive personal data under GDPR Art. 9. Pitching to [[alan]] (a regulated health insurer) means privacy is not optional: it's the first question their compliance team will ask.

## Legal framing

- **GDPR Art. 9** — health data is a "special category", requires explicit consent and a documented lawful basis.
- **CNIL "Référentiel santé"** — French regulator's framework for health-related apps; recommends data minimization, on-device processing where possible, EU-only storage.
- **HDS (Hébergeur de Données de Santé)** — required certification for any provider hosting French health data. Mistral La Plateforme is hosted in EU; HDS status must be confirmed before clinical use.

## V.I.T.A.L design choices

| Layer | Choice | Why it matters |
|-------|--------|----------------|
| HealthKit read | On-device, user-permissioned | Apple HealthKit never leaves the device without explicit user action |
| Voice STT | Voxtral via Mistral EU | EU data residency, no US transfer |
| LLM inference | Mistral Small 4 (EU) | No OpenAI / US provider in the loop |
| Storage | Self-hosted PostgreSQL | User controls retention and deletion |
| TTS | Voxtral (EU) | Same |
| Logs | No raw audio persisted, transcripts only | Minimization principle |

## Differentiation vs US health apps

- **Bevel** (see [[competitors]]) and most US wearable apps run inference on US servers — non-trivial GDPR risk for European employers.
- V.I.T.A.L's **all-EU stack** (Apple device + Mistral EU + self-hosted backend) is a structural moat in the FR/EU market, not a marketing claim.

## Open questions

- Does Mistral La Plateforme have HDS certification today, or is it on the roadmap?
- Can the FastAPI backend run inside Alan's own VPC for enterprise deployments?
- Voice recordings: how long do we retain transcripts? Recommendation: **0 days for raw audio, 30 days for transcripts, user-deletable**.

## Pitch one-liner

> "V.I.T.A.L est le seul coach burnout vocal 100% EU : Apple HealthKit on-device, Mistral hébergé en France, backend auto-hébergeable. Vos données santé ne quittent jamais l'Europe."

## Related Pages

- [[mistral]] — EU LLM provider, GDPR native
- [[alan]] — Health insurer, regulated context
- [[apple]] — HealthKit on-device model
- [[competitors]] — US alternatives and their data residency

## Sources to ingest

- CNIL "Référentiel applicatif santé" (TODO)
- Mistral DPA / hosting docs (TODO)
- HDS certification list — esante.gouv.fr (TODO)

---
**Status:** Draft  
**Confidence:** Medium
