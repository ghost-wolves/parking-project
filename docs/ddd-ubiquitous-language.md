# DDD Ubiquitous Language

This document captures domain terms used across contexts. Each term is defined **per context** where meanings may differ.
Where possible, the **Parking Management** context defines the base meaning.

---

## Core Terms

### Lot (Parking)
- **Meaning**: A named group of physical slots at a specific level (floor).  
- **Identity**: `lot_id`.  
- **Notes**: Lot may span multiple levels; in our service we parameterize by `level` for simplicity.

### Slot (Parking)
- **Meaning**: A physical parking space within a Lot and Level, reserved for either ICE or EV vehicles.  
- **Identity**: `(lot_id, level, index)`; UI-facing number is `slot_ui = index + 1`.  
- **States**: `VACANT`, `OCCUPIED` (see Slot state diagram).

### Vehicle (Parking/Accounts)
- **Meaning**: A road vehicle identified by a registration number.  
- **Identity**: `regnum` (unique within operator scope).  
- **Subtypes**: Car, Truck, Bus, Motorcycle; EV subtypes: ElectricCar, ElectricBike.  
- **Ownership**: Accounts context links vehicles to customers.

### VehicleSpec (Parking)
- **Meaning**: A *value object* that captures vehicle intent to park.  
- **Fields**: `regnum, make, model, color, fuel("ICE"|"EV"), kind`.  
- **Notes**: Passed from UI/CLI; service/factory chooses concrete class.

### Fuel (Parking/Charging)
- **Meaning**: Energy source for the vehicle. For Parking, used to choose pool (ICE/EV).  
- **Values**: `"ICE"`, `"EV"`.

### Slot UI Number (Parking)
- **Meaning**: 1-based slot number shown to humans.  
- **Notes**: Service converts internally to 0-based index via `_from_ui` and `_to_ui` helpers.

---

## Charging Terms (EV Charging)

### Charger
- **Meaning**: Physical EVSE device capable of delivering power to an EV.  
- **Identity**: `charger_id`.  
- **States**: `AVAILABLE`, `BUSY`, `OUT_OF_SERVICE`.

### Charging Session
- **Meaning**: A continuous energy delivery interval between an EV and a charger.  
- **Identity**: `session_id`.  
- **Lifecycle**: `STARTED` → `CLOSED` (with `kWh`, `duration`).  
- **Relations**: May reference `regnum` and `slot_ui` from Parking for correlation.

### Tariff
- **Meaning**: Pricing configuration used to rate a charging session.  
- **Identity**: `tariff_id`.  
- **Fields**: currency, base rate, tiers, time-of-day adjustments.

---

## Billing Terms (Billing & Payments)

### Invoice
- **Meaning**: A bill issued to a customer for parking and/or charging.  
- **Identity**: `invoice_id`.  
- **State**: `OPEN`, `PAID`, `VOID`.  
- **Composition**: `LineItem`s (parking time, kWh, fees).

### Payment
- **Meaning**: A monetary transaction applied to an invoice.  
- **Identity**: `payment_id`.  
- **State**: `AUTHORIZED`, `CAPTURED`, `FAILED`, `REFUNDED`.

### Line Item
- **Meaning**: Priced component (e.g., “2h parking”, “14.3 kWh”).  
- **Fields**: `type`, `qty`, `unit_price`, `total`.

---

## Accounts Terms (Customer & Accounts)

### Customer
- **Meaning**: A person or entity using the parking facility.  
- **Identity**: `customer_id`.  
- **Fields**: name, contact, auth credentials (stored securely).

### Vehicle Link
- **Meaning**: Association between a `customer_id` and a `regnum`.  
- **Notes**: Allows billing attribution and access control.

---

## Ops/Telemetry Terms (Operations & Telemetry)

### Telemetry Point
- **Meaning**: A time-stamped metric record (e.g., charger amps, availability).  
- **Identity**: `(metric, device_id, timestamp)`.

### Alert
- **Meaning**: A rule-driven signal that requires attention (e.g., `DeviceUnhealthy`).  
- **Fields**: severity, subject, message, timestamp.
