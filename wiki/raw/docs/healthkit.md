# Apple HealthKit – iOS Health Data (raw notes)

**Primary source**: https://developer.apple.com/documentation/HealthKit
**Reading date**: 2026-04-07
**Status**: raw (do not modify)

---

## Overview

- Apple framework for accessing health and fitness data on iOS/watchOS
- Centralizes data from all compatible apps and devices in the Health app
- Programmatic access via Swift API for authorized third-party apps

## Key Data Types for V.I.T.A.L (stress/burnout)

- **HRV**: key indicator of stress and nervous system recovery
- **Heart rate**: resting, active, variability
- **Sleep**: total duration, phases (REM, deep, light), quality
- **Physical activity**: steps, calories, workouts
- **Body temperature** (Apple Watch Series 8+)
- **SpO2**: oxygen saturation
- **Mindfulness**: meditation sessions, breathing time

## Permissions & Privacy

- Each data type requires explicit user permission
- Data stored locally on device (privacy by design)
- Background access possible for certain data types

## Unknown / To Confirm

- Is HRV available in real-time or only batch (overnight)?
- Which data is available without Apple Watch (iPhone only)?
- HealthKit API rate limits?