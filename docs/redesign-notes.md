# Redesign UML Audit (Structural vs Behavioral)

This folder contains the **redesign** diagrams:

- **Structural**
  - [`redesign-class.mmd`](./redesign-class.mmd) — shows `ParkingService`, `Slot`, `VehicleFactory`, and EV/ICE hierarchies, plus persistence methods.

- **Behavioral**
  - [`redesign-sequence-park.mmd`](./redesign-sequence-park.mmd) — dynamic flow for `ParkingService.park()`, including factory usage and 1-based slot IDs.
  - [`redesign-slot-state.mmd`](./redesign-slot-state.mmd) — `Slot` state machine (VACANT ↔ OCCUPIED).

## What changed from baseline

1. **Slot aggregate introduced**
   - Baseline used `None` sentinels in raw lists; redesign uses an explicit `Slot` with `occupy/free` invariants.

2. **Factory Method for vehicles**
   - UI no longer constructs concrete classes; `ParkingService` delegates to `VehicleFactory` (`ICE`/`EV` × kind).

3. **Clear UI ↔ Service contract**
   - UI passes `VehicleSpec` and always uses **1-based** slot numbers; service normalizes internally.

4. **Persistence + CSV**
   - Service now supports `to_dict()/from_dict()`, `save_json()/load_json()`, `save_csv()`.

5. **Finders standardized**
   - Consolidated ICE/EV finders and color/registration helpers for UI lookups.

## Structural vs Behavioral coverage

- **Structural**: class relationships, responsibilities, and composition (`ParkingService` ↔ `Slot`; factory wiring).
- **Behavioral**:
  - `park()` sequence captures creation/allocation messaging and error branches.
  - Slot state diagram codifies legal transitions and eliminates sentinel misuse.

These diagrams match the current, tested codebase.
