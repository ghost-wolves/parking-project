# Microservices Architecture

This document outlines a pragmatic microservices architecture for the Parking Lot system, aligned to the DDD bounded contexts.

> Goals: clear service boundaries, per‑service data ownership, simple APIs, and event‑driven integration where coupling would otherwise appear.

---

## Service Catalog (by bounded context)

| Service | Responsibility | Owns Data | External Dependencies |
|---|---|---|---|
| **parking-svc** | Manage lots & slots; park/leave; status & finders; CSV/JSON exports | Postgres: lots, slots, occupancy history | Accounts API (authN/authZ); emits events |
| **charging-svc** | Manage chargers & sessions; start/stop; track kWh | Postgres: chargers, sessions; (TS DB optional for raw meter) | Accounts API (authZ), Parking events |
| **billing-svc** | Invoices, line items, payments | Postgres: invoices, payments | Charging & Parking events; Payment provider |
| **accounts-svc** | Customers, vehicles, auth | Postgres: customers, vehicle links, credentials | — |
| **ops-svc** | Telemetry ingestion, derived metrics, alerts | Time‑series DB (e.g., Timescale/Influx); small Postgres for rules | Parking/Charging events |

---

## Ownership & Datastores

- **Per‑service DB**: no cross‑service table sharing.  
- **parking-svc**: Postgres (`lots`, `slots`, `events_occupancy`).  
- **charging-svc**: Postgres (`chargers`, `sessions`); optionally TS for meter readings.  
- **billing-svc**: Postgres (`invoices`, `line_items`, `payments`).  
- **accounts-svc**: Postgres (`customers`, `vehicles`, `credentials`).  
- **ops-svc**: TS DB for metrics + Postgres for alert definitions and incidents.

Backups & retention: short for operational tables, long for financial (billing).

---

## APIs (high-level)

### parking-svc
- `POST /lots/{id}/park` → `{ ok, slot_ui, message }`
- `POST /lots/{id}/leave` → `{ ok, message }`
- `GET /lots/{id}/status` → ICE + EV rows
- `GET /lots/{id}/status/ev` → EV rows only
- `GET /lots/{id}/export.csv` (optional proxy to exporter)

### charging-svc
- `POST /sessions` (start) → `{ session_id }`
- `PATCH /sessions/{id}/stop` → `{ kwh, duration }`
- `GET /chargers/{id}` → charger state

### billing-svc
- `POST /invoices` → `{ invoice_id }`
- `POST /invoices/{id}/lines` → add line item
- `POST /invoices/{id}/capture` → `{ status }`
- `GET /invoices/{id}`

### accounts-svc
- `POST /customers`, `GET /customers/{id}`
- `GET /customers/{id}/vehicles`
- `POST /auth/token` (OIDC/JWT)

### ops-svc
- `GET /metrics/occupancy`
- `GET /metrics/chargers/{id}`
- `POST /alerts/test` (for rule validation)

---

## Event Integration

- **parking-svc → charging-svc**: `VehicleParked`, `VehicleLeft`  
  used to correlate sessions with physical occupancy.
- **charging-svc → billing-svc**: `ChargingSessionClosed`  
  used to create CHARGING line items.
- **parking-svc → billing-svc (optional)**: `VehicleLeft` with duration for PARKING line items.
- **all → ops-svc**: events for metrics & alerts.

Event transport: Kafka, NATS, or lightweight SNS/SQS; at minimum, ensure **at‑least‑once** delivery and **idempotent** consumers.

---

## Security & Access

- **Auth**: `accounts-svc` issues JWTs (OIDC).  
- **AuthZ**: services validate scopes/roles (`parking:write`, `billing:read`, etc).  
- **PII**: keep minimal in domain events (e.g., `regnum` ok; avoid customer emails).  
- **Secrets**: vault/KMS for DB creds and provider keys.

---

## Observability

- **Logs**: structured JSON with correlation IDs (`x-correlation-id`).  
- **Metrics**: per‑service SLOs (latency, error rate); business KPIs (occupancy %, paid invoices).  
- **Tracing**: OpenTelemetry across gateways → services.

---

## Deployment Topology

- Containerize each service (Docker), deploy via K8s or compose‑based dev stack.  
- **Ingress**: API gateway (rate limits, JWT validation, routing).  
- **CI/CD**: per‑service pipelines; contracts tested with JSON schemas and consumer‑driven tests.

---

## Failure Modes & Resilience

- **parking-svc** remains available even if charging/billing are down (event buffering).  
- **charging-svc** can start sessions using stale account cache; reconcile later.  
- **billing-svc** is eventually updated through idempotent event consumers.  
- **ops-svc** tolerates delayed events; alerts have time windows.

---

## Example Event Schemas (concise)

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

**InvoicePaid**
```json
{
  "event": "InvoicePaid",
  "invoice_id": "inv_1001",
  "total": 11.58,
  "currency": "USD",
  "ts": "2025-09-21T16:02:01Z"
}
```

---

## Rollout Plan

1. Keep current monolith (`parking_service`) as **parking-svc** nucleus.  
2. Add **charging-svc** and publish/subscribe events (bridge internally first).  
3. Introduce **billing-svc** with ACL mapping from events → line items.  
4. Layer **accounts-svc** (JWTs) and **ops-svc** (metrics) as the system grows.
