# Codebase Checklist

## APIs
- [ ] Mistral API — LLM reasoning (mistral-large-3)
- [ ] Voxtral API — STT (voxtral-mini-latest)
- [ ] Voxtral or ElevenLabs API — TTS (voxtral-mini-tts-2603 / Flash v2.5)
- [ ] Thryve API — all health data (no local DB)
- [ ] Nebius API — Llama Guard 3 8B guardrail (block medical diagnosis)

## Web App
- [ ] FastAPI backend serves the web frontend
- [ ] Browser mic capture → send audio to backend
- [ ] Backend: audio → STT → LLM (with tools) → TTS → stream audio back
- [ ] Frontend plays audio response
- [ ] Clean UI on projector (full screen, no terminal)
- [ ] Works on any browser (no install needed for demo)

## LLM Tools (8)
- [ ] get_user_profile() — patient name, age, connected devices, blood panel
- [ ] get_vitals(days) — HRV (3100), resting HR (3001), sleep quality (2201), HR sleep (3002)
- [ ] get_blood_panel(days) — glucose (3302), HbA1c (3303), blood pressure (3300/3301)
- [ ] get_burnout_score() — compute from RMSSD + sleep + RHR + fetch SickLeavePrediction (2257)
- [ ] get_trend(metric, days) — compare recent vs baseline for one metric
- [ ] get_correlation(metric_a, metric_b, days) — cross two signals, detect compound risk
- [ ] award_berries(amount, reason) — log verifiable reward after checkup
- [ ] book_consultation(specialty, urgency, reason) — trigger consultation booking

## Feature 1: Weekly Vocal Checkup
- [ ] 3 structured questions via voice
- [ ] LLM pulls Thryve data mid-conversation via tools
- [ ] Contradiction detection: voice sentiment vs biometric signals
- [ ] Burnout score 0-100 generated and displayed
- [ ] Score formula: 100 - (45*RMSSD_norm + 35*Sleep_norm + 20*RHR_norm)

## Feature 2: Daily Adaptive Protocol
- [ ] Blood panel seeds weekly protocol (glucose, HbA1c, simulated ferritin/cortisol/vitD)
- [ ] Protocol = 3 concrete actions (nutrition, activity, sleep)
- [ ] Protocol adapts day-by-day as new wearable data comes in
- [ ] Show day 1 vs day 3 vs day 5 — protocol changed

## Feature 3: Daily Smart Nudge
- [ ] Biometric-triggered only (not scheduled)
- [ ] Triggers: HRV drop, RHR spike, sleep quality crash
- [ ] Short actionable message pushed to user

## Feature 4: Correlation Alert
- [ ] LLM crosses 2+ signals to flag compound risk
- [ ] Example: sleep dropping + glucose rising = metabolic stress
- [ ] Shown during checkup response

## Feature 5: Berries (Alan Play)
- [ ] Berries awarded after completing checkup
- [ ] Bonus berries for HRV baseline maintenance or sleep regularity streak
- [ ] Verifiable only — no self-reported rewards

## Data
- [ ] Real Thryve data on screen (not fake/hardcoded)
- [ ] Easy patient switchable (Thryve sandbox profiles)
- [ ] Device-agnostic: same code works for 22 wearable brands via Thryve
- [ ] Blood panel: glucose/HbA1c from Thryve + simulated ferritin/cortisol/vitD as JSON
- [ ] Confirm analytics codes (2257, 6406) availability with Thryve at hackathon
