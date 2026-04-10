---
title: Thryve Health Data API
created: 2026-04-10
updated: 2026-04-10
type: entity
tags: [partner, api-reference, health-data, wearables]
sources:
  - docs.thryve.health
---

# Thryve Health Data API

## Overview

Health data aggregation platform. Single API for 22 wearable sources (Fitbit, Garmin, Oura, Apple Health, Whoop, Withings, Samsung, Dexcom, etc.). Hackathon sandbox: ~10 user profiles, 1+ year real data.

## API Reference

### Base
- **URL:** `https://api.thryve.de/v5/`
- **Auth:** Two Basic Auth headers on every request:
  - `Authorization: Basic base64(username:password)` — global API
  - `AppAuthorization: Basic base64(authID:authSecret)` — per-app
- **Content-Type:** `application/x-www-form-urlencoded` (all POST)

### Endpoints

#### Create/Get User — `POST /v5/accessToken`
- Params: `partnerUserID` (optional alias)
- Returns: `accessToken` (text/plain)

#### User Info — `POST /v5/userInformation`
- Params: `authenticationToken`
- Returns: height, weight, birthdate, gender, connectedSources[], devices[]

#### Daily Data — `POST /v5/dailyDynamicValues`
- Max range: 364 days
- Params: `authenticationToken`, `startDay`/`endDay` (ISO 8601), `valueTypes` (comma-separated IDs), `dataSources`, `detailed`, `displayTypeName`
- Response:
```json
[{
  "authenticationToken": "...",
  "dataSources": [{
    "dataSource": 1,
    "data": [{
      "day": "2026-04-09T00:00:00Z",
      "dailyDynamicValueType": "1000",
      "dailyDynamicValueTypeName": "Steps",
      "value": "8523"
    }]
  }]
}]
```

#### Epoch (Intraday) Data — `POST /v5/dynamicEpochValues`
- Max range: 30 days
- Params: same as daily, uses `startTimestamp`/`endTimestamp`
- Response: same structure with `startTimestamp`, `endTimestamp`, `dynamicValueType`, `value`

### Webhooks (real-time push)
- Events: `event.data.epoch.create`, `event.data.daily.create`, etc.
- HTTPS port 443, Content-Encoding: zstd, must respond 200/204 in 2s
- HMAC secret for security, 3 retries then auto-disabled

## Data Type Mapping — V.I.T.A.L ↔ Thryve

| V.I.T.A.L Metric | Thryve ID | Thryve Name | Match |
|---|---|---|---|
| heart_rate | 3000 | HeartRate | EXACT |
| resting_hr | 3001 | HeartRateResting | EXACT |
| hrv | 3100 (epoch) / 3112 (daily) | Rmssd | DIRECT |
| spo2 | 3106 (epoch) / 3107 (daily) | SPO2 | EXACT |
| respiratory_rate | 5111 (epoch) / 5112 (daily) | RespirationRate | EXACT |
| wrist_temperature | 5041 | SkinTemperature | CLOSE |
| vo2_max | 3030 | VO2max | EXACT |
| walking_hr_avg | — | — | NO MATCH |
| steps | 1000 | Steps | EXACT |
| active_calories | 1011 | ActiveBurnedCalories | EXACT |
| resting_energy | 1016 | RestingMetabolicRate | EXACT |
| distance | 1001 | CoveredDistance | EXACT |
| workout | 1200 | ActivityType | PARTIAL |
| stand_time | — | — | NO MATCH |
| exercise_time | 1100 / 1114 | ActivityDuration | CLOSE |
| sleep | 2000 / 2300 | SleepDuration | EXACT |
| sleep_deep | 2003 / 2303 | SleepDeepDuration | EXACT |
| sleep_rem | 2002 / 2302 | SleepREMDuration | EXACT |
| audio_exposure | 8001 | AmbientAudioExposure | EXACT |
| mindful_minutes | — | — | NO MATCH |

**Coverage: 15/20 exact, 2 close, 3 missing**

## Bonus Burnout-Relevant Metrics (not in V.I.T.A.L yet)

| ID | Name | Why |
|---|---|---|
| 6010 | AverageStress | Direct stress score |
| 6011-6013 | Stress durations | Time in high/med/low stress |
| 2200 | SleepEfficiency | Clinical threshold at 75 |
| 2201 | SleepQuality | Clinical threshold at 77 |
| 2220 | SleepRegularity | Irregular sleep = burnout risk |
| 2254 | SleepRelatedMentalHealthRisk | Direct mental health risk |
| 6406 | MentalHealthRisk | Multi-dimensional risk score |
| 3113 | RmssdSleep | Overnight HRV recovery |

## Analytics (computed scores via same endpoint)

Filter by analytics DataType IDs in `dailyDynamicValues`:
- SleepQuality (2201), SleepEfficiency (2200), SleepRegularity (2220)
- PhysicalActivityIndex (1013), VO2maxPercentile (3032), FitnessAge (3031)
- SickLeavePrediction (2257), LifeExpectancyImpact (2258)
- MentalHealthRisk (6406)

## Supported Data Sources (22)

**Web/OAuth:** Fitbit, Garmin, Polar, Withings, Strava, Omron, Suunto, Oura, iHealth, Beurer, Huawei, Dexcom, Whoop, Decathlon, Komoot, FreeStyleLibre
**Native/SDK:** Apple Health, Samsung Health, Health Connect, ShenAI

---
**Status:** Ingested
**Confidence:** High
