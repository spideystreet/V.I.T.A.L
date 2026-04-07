---
title: Apple – HealthKit & Watch
created: 2026-04-07
updated: 2026-04-07
type: entity
tags: [platform, data-source]
sources:
  - healthkit.md
  - apple_coach.md
---

# Apple – HealthKit & Watch

## HealthKit Overview

Apple framework for accessing health/fitness data on iOS/watchOS.

- Centralizes data from all compatible apps/devices
- Programmatic access via Swift API for authorized 3rd-party apps
- Each data type requires explicit user permission
- Data stored locally on device (privacy by design)

## Key Data Types for V.I.T.A.L

| Data Type | Relevance |
|-----------|-----------|
| **HRV** | Key indicator of stress ([[hrv]]) |
| **Heart rate** | Resting, active, variability |
| **Sleep** | Duration-burnout link ([[sleep]]) |
| **Physical activity** | Steps, calories, workouts |
| **Body temperature** | Apple Watch Series 8+ |
| **SpO2** | Oxygen saturation |
| **Mindfulness** | Meditation sessions, breathing time |

## Apple AI Health Coach (Context)

- Apple was working on AI health coach integrated with Apple Watch/Health app
- **Project partially paused/reconfigured** (Feb 2026)
- Also working on health chatbot and health content studio
- **Implication:** V.I.T.A.L can occupy "mental health/stress coach via Apple Health" space Apple hasn't delivered yet

## Unknown / To Confirm
- Is HRV available in real-time or only batch (overnight)?
- Which data available without Apple Watch (iPhone only)?
- HealthKit API rate limits?
- Which Apple projects still active?

---
**Status:** Ingested  
**Confidence:** High