# Design Justification

## Purpose
Explain the redesign choices that improved correctness, testability, and maintainability. This document:
- Identifies **design patterns** we applied and why they fit.
- Calls out **anti-patterns** and smells we removed.
- Shows brief **before/after** deltas and impacts on tests.
- Connects decisions to the rubric’s “well-reasoned justification.”

---

## Summary of Problems in the Baseline
From the baseline UML and tests, the original design had several issues:

1. **Tight UI ↔ Domain Coupling**
   The Tk UI directly constructed concrete `Vehicle`/`ElectricVehicle` subclasses and passed them into the service, conflating presentation with domain creation.

2. **No Slot Abstraction**
   Parking capacity was modeled as `list[Any]` with `None` sentinels. This allowed illegal state transitions and scattered checks like “is this item `None`?” across code.

3. **Fragile Slot ID Semantics**
   The UI used **1-based** slot numbers; the service used **0-based**. Conversions were ad-hoc, causing off-by-one mistakes and unhelpful error messages.

4. **Inheritance Glitch in EV Classes (Baseline Defect)**
   Tests documented that EV subclasses didn’t correctly inherit/behave from the EV base in some cases.

5. **Testing Friction**
   Hard to unit-test construction/allocation decisions because object creation lived in the UI, not the domain.

---

## Patterns We Introduced (and Why)

### 1) Factory Method (`vehicle_factory.create`)
**Why**: Centralize vehicle instantiation decisions (fuel × kind) and decouple UI from concrete classes.
**Benefits**:
- UI passes a neutral `VehicleSpec`; the **service** decides the concrete class.
- Easier to test: construct specs and assert which subclass was produced.
- Extensible: adding `Bus`, `Truck`, or new EV types is a simple factory extension.

> **Where**: `src/vehicle_factory.py`, used inside `ParkingService.park()`.

### 2) State/Invariants via a Small Aggregate (`Slot`)
**Why**: Replace `None` sentinels with an explicit Slot that owns its occupancy rules.
**Benefits**:
- `Slot.occupy()`/`free()` encode legal transitions (VACANT ↔ OCCUPIED).
- Eliminates scattered “is None?” checks; reduces accidental overwrite of occupied slots.
- Clearer status reporting and invariant enforcement (validated by tests).

> **Where**: `src/slot.py`, with a simple state machine (VACANT/OCCUPIED).

### 3) Service Façade with Thin UI
**Why**: Keep UI as an adapter for inputs/outputs and push logic into `ParkingService`.
**Benefits**:
- UI is test-agnostic; service can be fully unit-tested without Tk.
- Stable public surface: `park(spec)`, `leave(slot_ui, fuel)`, `status_rows()`, EV finders, etc.
- Consistent **1-based** slot numbers in responses; service handles normalization.

> **Where**: `src/parking_service.py` public methods and helpers.

### 4) Persistence Boundary (Serialization/CSV)
**Why**: Separate I/O (JSON/CSV) from UI; allow save/load and export across UI & CLI.
**Benefits**:
- Deterministic round-trips (`to_dict`/`from_dict`, `save_json`/`load_json`).
- CSV export for graders/users; straightforward test coverage.

> **Where**: `ParkingService.to_dict/from_dict/save_json/load_json/save_csv`.

### 5) Defensive Input Normalization
**Why**: Normalize reg/make/model/color in UI to reduce user-driven inconsistency.
**Benefits**:
- Fewer “phantom misses” in lookups; better UX and test determinism.

> **Where**: `ParkingManager.py` (UI builds `VehicleSpec` with stripped/uppercased `regnum`).

---

## Anti-Patterns / Smells Removed

| Baseline Smell / Anti-pattern | Fix |
|---|---|
| UI constructs domain objects (tight coupling) | **Factory Method** + `VehicleSpec` DTO; UI no longer depends on concrete classes. |
| `None` sentinels in lists (implicit state) | **`Slot`** abstraction with `occupy()` / `free()` and a tiny state machine. |
| Off-by-one slot confusion | `_to_ui` / `_from_ui` helpers; service guarantees **1-based** externally. |
| Global Tk state & side effects at import time | UI creates Tk objects **only in `main()`**; helpers return buttons for enabling/disabling. |
| Scattered string handling & weak messages | Centralized validation; consistent messages in `ParkingService`. |
| Unclear EV inheritance | Factory enforces the correct class; tests validate behavior through the service. |
| Difficult to persist | JSON/CSV methods on the service; UI and CLI reuse. |

---

## Before/After (Tiny Illustrations)

### Construction (Before → After)
**Before (UI):**
```python
# UI directly constructing concrete class
if is_ev:
    vehicle = ElectricCar(reg, make, model, color)
else:
    vehicle = Car(reg, make, model, color)
service.park(vehicle)  # implicit choices live in the UI
```

**After (Service via Factory):**
```python
# UI provides spec; service decides concrete type
res = service.park(VehicleSpec(reg, make, model, color, fuel, kind))
# inside service:
vehicle = vehicle_factory.create(reg, make, model, color, fuel, kind)
slot.occupy(vehicle)
```

### Slot State (Before → After)
**Before:**
```python
# lists with None sentinels
if slots[i] is None:
    slots[i] = vehicle
else:
    # accidental overwrite risk or scattered checks
```

**After:**
```python
# explicit state transitions
if slot.is_vacant:
    slot.occupy(vehicle)  # raises if illegal
else:
    raise ValueError("Slot occupied")
```

### Slot Numbering (Before → After)
**Before:** ad-hoc `ui-1` sprinkled in multiple places.
**After:** `_to_ui(idx)` and `_from_ui(ui)` centralize normalization in `ParkingService`.

---

## Why These Choices Fit *This* Problem
- **Factory Method** decouples “what to build” from “who uses it.” We don’t need a full Abstract Factory; a single `create` is enough here.
- **Slot** as an aggregate for occupancy is a domain concept users understand; encoding it directly reduces bugs more than documenting “remember to check `None`.”
- **Service Façade** keeps logic in one place, enabling focused tests and stable UI/CLI integration.
- **Persistence** at the domain boundary enables scenario replay and regression testing.

---

## Trade-offs & Alternatives Considered
- **Keep raw lists + `None`**, add more checks → still brittle; invariants remain implicit. `Slot` clarifies and enforces intent.
- **Abstract Factory/Strategy for every subclass combination** → over-engineering for this domain size; a simple `create` is clearer.
- **Domain events now** → out of scope; noted for microservices. Current service is synchronous and sufficient.

---

## Impact on Testing & Quality
- **Unit tests** target `ParkingService` for park/leave/status/finders and persistence.
- **UI tests** minimal; the UI is a thin adapter.
- **Coverage**: CSV/JSON round-trips are deterministic and easy to verify.
- **Static typing**: mypy coverage increased, reducing runtime surprises.

---

## Rubric Alignment (at a glance)
- **Discussed patterns & why**: Factory Method, Slot state/invariants, Service Façade, input normalization.
- **Removed anti-patterns**: globals, sentinels, ad-hoc slot math, UI-domain coupling.
- **Justification depth**: includes trade-offs, alternatives, and testing impact.
- **Artifacts cross-referenced**: baseline/redesign UMLs, tests, and code locations.

---

## References to Artifacts
- **Baseline UML**: `docs/original_class.mmd`, `docs/original_sequence_park.mmd`, `docs/original_sequence_leave.mmd`
- **Redesign UML**: `docs/redesign-class.mmd`, `docs/redesign-sequence-park.mmd`, `docs/redesign-slot-state.mmd`
- **Code**: `src/parking_service.py`, `src/slot.py`, `src/vehicle_factory.py`, `src/Vehicle.py`, `src/ElectricVehicle.py`
- **UI/CLI**: `src/ParkingManager.py`, `src/cli.py`
- **Tests**: `tests/` (service behavior, slot normalization, factory usage, persistence)
