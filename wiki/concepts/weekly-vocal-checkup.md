---
title: Weekly Vocal Check-up
created: 2026-04-07
updated: 2026-04-08
type: concept
tags: [voice-biomarker, implementation, ritual]
sources:
  - alan_pressroom.md
---

# Weekly Vocal Check-up

## Concept

- **What:** A short (~2 min) structured voice conversation, once a week, that crosses subjective state (how the user feels) with objective HealthKit data (HRV, sleep, resting HR, steps) to produce a stress/burnout score and one concrete recommendation.
- **Why:** [[alan]] Play shows **26% weekly engagement** on a gamified prevention app — a weekly ritual is the proven cadence for this audience. Daily is too noisy for HRV/sleep trends; monthly is too late to prevent burnout.
- **When:** Sunday evening or Monday morning by default, user-configurable. Push notification from the Watch.

## User Flow

1. **Trigger** — Watch notification: "Ton checkup hebdo V.I.T.A.L est prêt."
2. **Greeting** — V.I.T.A.L summarizes the week's biometrics in one sentence ("HRV moyenne 42 ms, sommeil 6h30, 8200 pas/jour").
3. **Subjective Q1** — "Sur une échelle de 1 à 10, ton niveau d'énergie cette semaine ?"
4. **Subjective Q2** — "Qu'est-ce qui t'a le plus pesé cette semaine ?"
5. **Subjective Q3** — "Tu as réussi à décrocher du travail le soir ?"
6. **Synthesis** — V.I.T.A.L cross-references answers with biometric trends, names the pattern (e.g. "stress chronique léger : HRV en baisse + sommeil court + sentiment de surcharge"), gives a score 0–100.
7. **Action** — One concrete recommendation: respiration, marche, ou — si signaux persistants — proposer `book_consultation` (psy Alan, 100% remboursé).

## Voice Biomarkers Measured

- **Objective (HealthKit, see [[hrv]], [[sleep]]):** 7-day HRV trend, avg sleep duration, resting HR, steps, mindful minutes.
- **Subjective (voice content):** energy level (1–10), stressor identification, work-life detachment.
- **Future (voice signal, see [[voice-biomarkers]]):** prosody / speech rate as fatigue proxy — out of scope for hackathon.

## Output

- **Score:** 0–100 burnout risk index, with 3 bands (vert / orange / rouge).
- **Insights:** 2–3 sentences naming the dominant pattern, citing real numbers.
- **Recommendations:** exactly one actionable step. If red band 2 weeks in a row → propose `book_consultation`.

## Engagement Strategy

- **Streak:** count consecutive weekly checkups completed (see [[gamification]]).
- **Trend card:** show score evolution week-over-week on the iPhone app.
- **Alan integration angle:** weekly checkup completion could earn Alan Play berries — pitch-only for hackathon.

## Implementation Notes

- New mode in `vital/brain.py`: `weekly_checkup` flag in system prompt that switches the LLM from reactive Q&A to a structured 3-question script.
- The LLM still has access to all 6 tools — the `get_health_trend` and `get_health_summary(168)` calls are mandatory at step 2.
- Score computation: simple weighted formula in Python, not LLM-generated, so it's reproducible.

## Related Pages

- [[voice-biomarkers]] — Technical basis
- [[gamification]] — Engagement layer
- [[hrv]] — Primary biomarker
- [[sleep]] — Secondary biomarker
- [[burnout]] — What we're detecting
- [[alan]] — Weekly engagement benchmark (26%)

---
**Status:** Spec  
**Confidence:** Medium
