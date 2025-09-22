# API Sketch & Data Contracts

This document outlines pragmatic HTTP APIs and event contracts for each service. Schemas are provided as **JSON Schema**-style snippets (informal) to guide implementation and contract tests.

> Conventions: JSON over HTTPS; snake_case for fields; `id` fields are strings; times are ISO-8601 UTC; 1-based `slot_ui` in Parking. All write endpoints are **idempotent** where noted.

---

## 1) parking-svc

### 1.1 `POST /lots/{lot_id}/park`
Park a vehicle into the EV or ICE pool.
- **Idempotency**: Supply `Idempotency-Key` header to dedupe retries.
- **Request**
```json
{
  "level": 1,
  "spec": {
    "regnum": "ABC123",
    "make": "Tesla",
    "model": "Model 3",
    "color": "Blue",
    "fuel": "EV",
    "kind": "CAR"
  }
}
```
- **Response `200`**
```json
{
  "ok": true,
  "slot_ui": 3,
  "message": "Allocated EV slot 3 on level 1"
}
```
- **Response `409`** (full)
```json
{ "ok": false, "error": "EV_LOT_FULL", "message": "EV lot is full" }
```
- **Errors**: `400` invalid spec; `404` lot/level not found.

**Schema (sketch)**
```json
{
  "type": "object",
  "required": ["level", "spec"],
  "properties": {
    "level": { "type": "integer", "minimum": 1 },
    "spec": {
      "type": "object",
      "required": ["regnum","make","model","color","fuel","kind"],
      "properties": {
        "regnum": { "type": "string", "minLength": 1 },
        "make": { "type": "string" },
        "model": { "type": "string" },
        "color": { "type": "string" },
        "fuel": { "enum": ["ICE","EV"] },
        "kind": { "enum": ["CAR","MOTORCYCLE","BUS","TRUCK"] }
      }
    }
  }
}
```

### 1.2 `POST /lots/{lot_id}/leave`
Remove a vehicle from a slot (UI numbering).
- **Request**
```json
{ "level": 1, "slot_ui": 3, "fuel": "EV" }
```
- **Response `200`**
```json
{ "ok": true, "message": "Slot 3 freed" }
```
- **Response `404`** (invalid slot or empty)
```json
{ "ok": false, "error": "INVALID_SLOT", "message": "No vehicle in slot 3" }
```

### 1.3 `GET /lots/{lot_id}/status`
Return both ICE and EV rows (for UI).
- **Query**: `?level=1` (required)
- **Response `200`**
```json
{
  "ice": [
    { "slot_ui": 1, "level": 1, "regnum": "R1", "color": "Blue", "make": "Honda", "model": "Civic" }
  ],
  "ev": [
    { "slot_ui": 1, "level": 1, "regnum": "E1", "color": "Red", "make": "Tesla", "model": "Model 3", "charge": 0 }
  ]
}
```

### 1.4 `GET /lots/{lot_id}/status/ev`
- **Query**: `?level=1`
- **Response**: array of EV rows (same row shape as `ev` above).

### 1.5 Events (parking-svc)
Emitted on successful commands.

**VehicleParked**
```json
{
  "event": "VehicleParked",
  "lot_id": "A1",
  "level": 1,
  "slot_ui": 3,
  "regnum": "ABC123",
  "fuel": "EV",
  "kind": "CAR",
  "ts": "2025-09-21T14:33:05Z"
}
```
**VehicleLeft**
```json
{
  "event": "VehicleLeft",
  "lot_id": "A1",
  "level": 1,
  "slot_ui": 3,
  "regnum": "ABC123",
  "fuel": "EV",
  "ts": "2025-09-21T15:00:00Z"
}
```

---

## 2) charging-svc

### 2.1 `POST /sessions`
Start a charging session.
- **Request**
```json
{
  "charger_id": "CH_12",
  "regnum": "ABC123",
  "slot_ui": 3,
  "lot_id": "A1",
  "tariff_id": "T_STD"
}
```
- **Response `201`**
```json
{ "session_id": "sess_9f2" }
```
- **Errors**: `409` if charger busy; `404` charger not found.

### 2.2 `PATCH /sessions/{id}/stop`
Stop a session; returns totals.
- **Request**: `{}` (or `{ "reason": "user_stop" }`)
- **Response `200`**
```json
{ "kwh": 14.3, "duration_sec": 1860, "tariff_id": "T_STD" }
```
- **Errors**: `404` session not found; `409` already closed.

### 2.3 `GET /chargers/{id}`
- **Response**
```json
{
  "charger_id": "CH_12",
  "state": "BUSY",
  "power_kw": 50.0,
  "location": "L1-NE"
}
```

### 2.4 Events (charging-svc)

**ChargingSessionStarted**
```json
{
  "event": "ChargingSessionStarted",
  "session_id": "sess_9f2",
  "charger_id": "CH_12",
  "regnum": "ABC123",
  "slot_ui": 3,
  "lot_id": "A1",
  "tariff_id": "T_STD",
  "ts": "2025-09-21T14:35:00Z"
}
```

**ChargingSessionClosed**
```json
{
  "event": "ChargingSessionClosed",
  "session_id": "sess_9f2",
  "charger_id": "CH_12",
  "regnum": "ABC123",
  "kwh": 14.3,
  "duration_sec": 1860,
  "tariff_id": "T_STD",
  "ts": "2025-09-21T15:12:10Z"
}
```

---

## 3) billing-svc

### 3.1 `POST /invoices`
Create an invoice.
- **Request**
```json
{ "customer_id": "cust_77", "currency": "USD" }
```
- **Response `201`**
```json
{ "invoice_id": "inv_1001", "status": "OPEN" }
```

### 3.2 `POST /invoices/{id}/lines`
Add a line item (OPEN invoices only).
- **Request**
```json
{
  "type": "CHARGING",
  "qty": 14.3,
  "unit_price": 0.25,
  "metadata": { "session_id": "sess_9f2", "charger_id": "CH_12" }
}
```
- **Response `200`**
```json
{ "ok": true }
```
- **Errors**: `409` if invoice is not OPEN.

### 3.3 `POST /invoices/{id}/capture`
Capture payment for the full total (or partial—if allowed).
- **Request**
```json
{ "amount": 11.58, "currency": "USD", "provider_ref": "pi_1234" }
```
- **Response `200`**
```json
{ "status": "PAID" }
```

### 3.4 `GET /invoices/{id}`
- **Response**
```json
{
  "invoice_id": "inv_1001",
  "status": "PAID",
  "currency": "USD",
  "line_items": [
    { "type": "PARKING", "qty": 2.0, "unit_price": 4.00, "total": 8.00 },
    { "type": "CHARGING", "qty": 14.3, "unit_price": 0.25, "total": 3.575 }
  ],
  "total": 11.575
}
```

### 3.5 Events (billing-svc)

**InvoiceCreated**
```json
{ "event": "InvoiceCreated", "invoice_id": "inv_1001", "customer_id": "cust_77", "ts": "2025-09-21T15:30:00Z" }
```
**InvoicePaid**
```json
{ "event": "InvoicePaid", "invoice_id": "inv_1001", "total": 11.58, "currency": "USD", "ts": "2025-09-21T16:02:01Z" }
```

---

## 4) accounts-svc

### 4.1 `POST /customers`
- **Request**
```json
{ "name": "Ada Lovelace", "email": "ada@example.com" }
```
- **Response `201`**
```json
{ "customer_id": "cust_77" }
```

### 4.2 `GET /customers/{id}`
- **Response**
```json
{ "customer_id": "cust_77", "name": "Ada Lovelace", "email": "ada@example.com" }
```

### 4.3 `GET /customers/{id}/vehicles`
- **Response**
```json
{ "items": [ { "regnum": "ABC123", "nickname": "Daily Driver" } ] }
```

### 4.4 `POST /auth/token`
- **Request**: `{ "username": "...", "password": "..." }`
- **Response**: `{ "access_token": "JWT...", "expires_in": 3600 }`

---

## 5) Common Concerns

### Versioning
- Use `/v1/...` path prefix or `Accept: application/vnd.parking.v1+json`.
- Breaking changes require a new version.

### Errors
- Problem+JSON style:
```json
{
  "type": "about:blank",
  "title": "Conflict",
  "status": 409,
  "detail": "EV lot is full",
  "code": "EV_LOT_FULL"
}
```

### Security
- OAuth2/OIDC bearer tokens from `accounts-svc` (`Authorization: Bearer ...`).
- Scopes: `parking:write`, `parking:read`, `charging:write`, `billing:read`, etc.

### Idempotency
- For `POST` commands that **change state**, clients may send `Idempotency-Key` header. Servers must store keys with response hashes for a time window (e.g., 24h).

### Pagination
- `GET` collections: `?limit=50&cursor=abc` with `next_cursor` in response.

---

## 6) cURL Examples

```bash
# Park a vehicle (EV)
curl -X POST "https://api.example.com/v1/lots/A1/park" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: 1c1a2e-park-abc123" \
  -d '{ "level":1, "spec":{"regnum":"ABC123","make":"Tesla","model":"Model 3","color":"Blue","fuel":"EV","kind":"CAR"} }'

# Stop a charging session
curl -X PATCH "https://api.example.com/v1/sessions/sess_9f2/stop" \
  -H "Authorization: Bearer $TOKEN"

# Create invoice and add a charging line
curl -X POST "https://api.example.com/v1/invoices" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{ "customer_id":"cust_77", "currency":"USD" }'
curl -X POST "https://api.example.com/v1/invoices/inv_1001/lines" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{ "type":"CHARGING","qty":14.3,"unit_price":0.25,"metadata":{"session_id":"sess_9f2","charger_id":"CH_12"} }'
curl -X POST "https://api.example.com/v1/invoices/inv_1001/capture" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{ "amount": 11.58, "currency":"USD", "provider_ref":"pi_1234" }'
```

---

## 7) Validation & Testing

- **JSON Schema** validation in gateways (ajv/fastjsonschema).  
- **Consumer-driven contract tests** (e.g., Pact) between Parking ↔ Charging ↔ Billing.  
- **Event idempotency tests** ensuring duplicates do not double-bill or double-park.  
- **Security tests**: scope checks, token expiry.

