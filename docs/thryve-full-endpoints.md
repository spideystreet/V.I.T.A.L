# Thryve Health API -- Complete Endpoint Reference

> Compiled from [docs.thryve.health](https://docs.thryve.health/) sitemap crawl, 2026-04-10.
> Base URL: `https://api.thryve.de`

---

## Authentication (all endpoints)

Every request requires two Basic Auth headers:

| Header | Value |
|--------|-------|
| `Authorization` | `Basic base64(username:password)` |
| `AppAuthorization` | `Basic base64(authID:authSecret)` |

---

## 1. POST /v5/accessToken -- Create or Get User

**In MCP:** YES (`create_user`)

Creates a new user or retrieves the token for an existing user.

**Content-Type:** `application/x-www-form-urlencoded`

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `partnerUserID` | string | no | Your alias for the user. If absent, a new user is always created. If set and matches existing, returns existing token. |

**Response 200:** plain text -- the `authenticationToken` string.
**Response 400:** JSON error.

---

## 2. POST /v5/dailyDynamicValues -- Get Daily Data

**In MCP:** YES (`get_daily_values`, `get_burnout_metrics`, `get_sleep_analysis`, `get_risk_assessment`, `get_vital_summary`)

Aggregated daily data (one value per metric per day).

**Content-Type:** `application/x-www-form-urlencoded`

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `authenticationToken` | string | yes | Per-user token |
| `startDay` | string | yes* | ISO 8601 date |
| `endDay` | string | yes* | ISO 8601 date |
| `startTimestampUnix` | int | alt* | Milliseconds |
| `endTimestampUnix` | int | alt* | Milliseconds |
| `valueTypes` | string | no | Comma-separated data type IDs |
| `dataSources` | string | no | Comma-separated source IDs |
| `detailed` | bool | no | Include recording metadata |
| `displayTypeName` | bool | no | Include type name |
| `displayPartnerUserID` | bool | no | Include alias |

*One date pair required. ISO wins if both provided. Max range: 364 days.

**Response 200:** JSON array of `{ authenticationToken, partnerUserID, dataSources: [{ dataSource, data: [{ day, timestampUnix, createdAt, createdAtUnix, dailyDynamicValueType, dailyDynamicValueTypeName, value, valueType, details }] }] }`

---

## 3. POST /v5/dynamicEpochValues -- Get Epoch (Intraday) Data

**In MCP:** YES (`get_epoch_values`)

Per-measurement data with second-level precision.

**Content-Type:** `application/x-www-form-urlencoded`

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `authenticationToken` | string | yes | Per-user token |
| `startTimestamp` | string | yes* | ISO 8601 datetime |
| `endTimestamp` | string | yes* | ISO 8601 datetime |
| `startTimestampUnix` | int | alt* | Milliseconds |
| `endTimestampUnix` | int | alt* | Milliseconds |
| `valueTypes` | string | no | Comma-separated data type IDs |
| `dataSources` | string | no | Comma-separated source IDs |
| `detailed` | bool | no | Include recording metadata |
| `displayTypeName` | bool | no | Include type name |
| `displayPartnerUserID` | bool | no | Include alias |

*One timestamp pair required. Max range: 30 days.

**Response 200:** JSON array of `{ authenticationToken, partnerUserID, dataSources: [{ dataSource, data: [{ startTimestamp, endTimestamp, startTimestampUnix, endTimestampUnix, createdAt, createdAtUnix, dynamicValueType, dynamicValueTypeName, value, valueType, details }] }] }`

---

## 4. POST /v5/userInformation -- Get End User Information

**In MCP:** NO

Retrieves user profile and connected data sources.

**Content-Type:** `application/x-www-form-urlencoded`

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `authenticationToken` | string | yes | Per-user token |

**Response 200:** JSON array:

```json
[{
  "authenticationToken": "...",
  "partnerUserID": "...",
  "height": 175,
  "weight": 72.5,
  "birthdate": "1990-01-15",
  "gender": "male",
  "connectedSources": [
    { "dataSource": 5, "connectedAt": "2026-04-01T10:00:00Z" }
  ],
  "devices": [
    {
      "dataSource": 5,
      "deviceName": "Apple Watch",
      "connectedAt": "2026-04-01T10:00:00Z",
      "configuration": {}
    }
  ]
}]
```

---

## 5. PUT /v5/userInformation -- Update End User Information

**In MCP:** NO

Updates user profile (height, weight, birthdate, gender). These values feed into analytics like BMI, VO2max, and FitnessAge.

**Content-Type:** `application/json`

**Headers (additional):**
- `authenticationToken` as header (not body)

**Request body:**

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `height` | int | no | Centimeters |
| `weight` | float | no | Kilograms |
| `birthdate` | string | no | `YYYY-MM-DD` |
| `gender` | string | no | `male`, `female`, `genderless` |

**Response 204:** Success, no body.
**Response 400:** JSON error.

---

## 6. DELETE /v5/userInformation -- Delete End User

**In MCP:** NO

Schedules user deletion. Data remains queryable until midnight UTC on the deletion date.

**Content-Type:** `application/x-www-form-urlencoded`

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `authenticationToken` | string | yes | Comma-separated tokens to delete multiple users |
| `deletionDate` | string | no | ISO 8601 date. Defaults to 7 days ahead. |

**Response 204:** Added to deletion queue.
**Response 400:** JSON error.

---

## 7. POST /widget/v6/connection -- Get Connection Widget URL

**In MCP:** NO

Returns a URL to embed the Thryve connection widget (iframe) so users can connect/disconnect wearables.

**Content-Type:** `application/json`

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| `endUserId` | string | yes | User token |
| `locale` | string | no | ISO 639-1 code (en, de, fr, es, ...) |

**Response 200:**

```json
{
  "type": "enduser.widget.connection",
  "data": {
    "url": "https://connect.thryve.de/?connectionSessionToken=TOKEN&..."
  }
}
```

The URL expires. Must be embedded in an iframe, not opened in a new tab.

---

## 8. POST /v5/dataSourceURL -- Get Connection Widget URL (DEPRECATED)

**In MCP:** NO

Legacy version of endpoint 7.

**Content-Type:** `application/x-www-form-urlencoded`

| Param | Type | Required | Notes |
|-------|------|----------|-------|
| `authenticationToken` | string | yes | Per-user token |

**Response 200:** plain text URL to the connection widget.

---

## 9. Custom Data Source Connection (Web flow, no single REST endpoint)

**In MCP:** NO -- not applicable (browser flow)

After obtaining a `connectionSessionToken` from endpoint 7, you can build custom connection UIs using these URLs:

| URL | Method | Purpose |
|-----|--------|---------|
| `https://service2.und-gesund.de/dataSourceDirectConnection.html?token=TOKEN&dataSource=ID&redirect_uri=URI` | GET | Connect a specific data source |
| `https://service2.und-gesund.de/dataSourceDirectRevoke.html?token=TOKEN&dataSource=ID&direct=true&redirect_uri=URI` | GET | Disconnect a data source |
| `https://service2.und-gesund.de/dataSourceDirectConnectionResult.html?token=TOKEN&dataSource=ID&connected=BOOL` | GET (redirect) | Connection result callback |

---

## Webhooks (configured in Thryve Dashboard, not API)

Thryve pushes data to your HTTPS endpoint (port 443). Must return 200/204 within 2 seconds. Up to 3 retries on failure.

### Data Push Webhooks

Your endpoint receives POST requests with:
- `Content-Type: application/json`
- `Content-Encoding: zstd`

| Event Type | Trigger |
|-----------|---------|
| `event.data.epoch.create` | New epoch data stored |
| `event.data.epoch.update` | Existing epoch data updated |
| `event.data.daily.create` | New daily data stored |
| `event.data.daily.update` | Existing daily data updated |

**Payload:** `{ endUserId, endUserAlias, timestampType, type, data: [{ dataSource, data: [...] }] }`

### Notification Webhooks (lightweight)

| Event Type | Trigger |
|-----------|---------|
| `notification.source.connect` | User connected a data source |
| `notification.source.disconnect` | User disconnected a data source |
| `notification.data.epoch.createupdate` | Epoch data created or updated |
| `notification.data.daily.createupdate` | Daily data created or updated |

**Epoch notification payload:** `{ endUserId, endUserAlias, timestampType, type, startTimestamp, endTimestamp, dataSourceId, dataTypeIds: [] }`

**Daily notification payload:** `{ endUserId, endUserAlias, timestampType, type, startDay, endDay, dataSourceId, dataTypeIds: [] }`

**Source notification payload:** `{ endUserId, endUserAlias, dataSourceId, timestamp }`

---

## SDK-Only Methods (no REST endpoints)

These are native SDK calls, not HTTP APIs:

| Method | Platform | Purpose |
|--------|----------|---------|
| `ThryveSDK.getOrCreate(config)` | iOS/Android/RN/Flutter | Initialize SDK |
| `getEndUserId()` | All | Get current user token |
| `ThryveDataSourceConnectionWidget` | All | Show connection UI |
| `executeBackgroundSync()` | All | Manual background data sync |
| `ThryveBLEEventListener.onHeartRateDataReceived()` | iOS/Android | Real-time HR from BLE monitors |

---

## Summary: What's Missing from Our MCP

| # | Endpoint | Method | In MCP? | Priority for V.I.T.A.L |
|---|----------|--------|---------|------------------------|
| 4 | `/v5/userInformation` | POST (get) | NO | **HIGH** -- needed to check connected sources and set user profile for accurate analytics |
| 5 | `/v5/userInformation` | PUT (update) | NO | **HIGH** -- setting height/weight/birthdate/gender improves VO2max, BMI, FitnessAge accuracy |
| 6 | `/v5/userInformation` | DELETE | NO | **MEDIUM** -- GDPR compliance, user account deletion |
| 7 | `/widget/v6/connection` | POST | NO | **LOW** -- web widget, not needed for native iOS app (SDK handles connections) |
| 8 | `/v5/dataSourceURL` | POST | NO | SKIP -- deprecated |
| -- | Webhook receiver | -- | NO | **HIGH** -- we should set up a webhook endpoint in `health_server.py` to receive real-time data pushes instead of polling |

### Recommended additions to `thryve_mcp.py`:

1. **`get_user_info(auth_token)`** -- POST `/v5/userInformation` -- check connected sources, profile completeness
2. **`update_user_info(auth_token, height, weight, birthdate, gender)`** -- PUT `/v5/userInformation` -- improve analytics accuracy
3. **`delete_user(auth_token, deletion_date)`** -- DELETE `/v5/userInformation` -- GDPR

### Recommended additions to `health_server.py`:

4. **Webhook endpoint** -- receive `event.data.daily.create` and `event.data.epoch.create` pushes from Thryve instead of polling

---

*Source: full sitemap crawl of docs.thryve.health (50 pages) -- 2026-04-10*
