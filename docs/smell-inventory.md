# Smell & Defect Inventory (Baseline)
Scope: `src/ParkingManager.py`, `src/Vehicle.py`, `src/ElectricVehicle.py`

> Purpose: Document concrete issues in the **original** code and tie each to a fix and a test idea. This anchors the rubric’s “identify bad practices” and will be referenced in the justification paper.

---

## 1) EV subclasses don’t inherit from `ElectricVehicle` (**bug**)
**Files/Lines:** `src/ElectricVehicle.py` (classes `ElectricCar`, `ElectricBike` declared without a base)  
**Why it’s a problem:** `isinstance(ElectricCar(), ElectricVehicle)` is `False`; shared behavior duplicated; polymorphism and future extensions break.  
**Fix:** Declare `class ElectricCar(ElectricVehicle): ...` and `class ElectricBike(ElectricVehicle): ...`. Ensure `super().__init__` is called.  
**Test idea:** Construct each; assert `isinstance(..., ElectricVehicle)` and that `getType()` and EV fields read correctly.

---

## 2) Wrong variable used in EV search helpers (**bug**)
**Files/Lines:** `src/ParkingManager.py` (EV finders use undefined `make`/`model` while the parameter is named `color`)  
**Why it’s a problem:** Raises `NameError` or silently returns wrong slots.  
**Fix:** Rename parameters to `make` / `model` and compare against the correct variable; add type hints.  
**Test idea:** Seed known EV vehicles into slots and assert the function returns expected indices.

---

## 3) Slot ID confusion: counters vs indices (**bug/design**)
**Files/Lines:** `src/ParkingManager.py` (dual counters `slotid`/`slotEvId` used alongside array indices)  
**Why it’s a problem:** The “slot shown to user” can diverge from actual storage index; `leave()` may free the wrong slot.  
**Fix:** Use the **array index** as the canonical ID (0‑based internal). Present 1‑based to UI via helpers `to_ui_id(idx)` / `from_ui_id(n)`. Remove separate counters.  
**Test idea:** Park → capture shown slot → `leave()` with that slot → assert the same slot is freed.

---

## 4) Vehicle type mix‑ups in creation branches (**bug**)
**Files/Lines:** `src/ParkingManager.py` (branches pick `Car` when motorcycle was chosen; EV/non‑EV bike/car confusion)  
**Why it’s a problem:** Instances have the wrong class; filters and reports lie.  
**Fix:** Centralize creation behind a **VehicleFactory** that maps `(fuel=EV|ICE, kind=CAR|MOTORCYCLE|BUS)` to the correct subclass.  
**Test idea:** Parametrized matrix test for each combination → assert `type(instance)` matches expectation.

---

## 5) Severe UI/domain coupling (**design smell**)
**Files/Lines:** `src/ParkingManager.py` (domain methods reference Tk widgets, globals)  
**Why it’s a problem:** Hard to unit test; can’t reuse domain in other UIs/services; fragile imports.  
**Fix:** Introduce `ParkingService` façade. Domain returns data/DTOs; GUI renders text. Kill Tk imports from domain modules.  
**Test idea:** Domain unit tests import with **no** Tk present; verify outputs as plain data.

---

## 6) Magic sentinel values (`-1`) & primitive obsession (**design smell**)
**Files/Lines:** `src/ParkingManager.py` (arrays scanned for `-1` to find empty slots)  
**Why it’s a problem:** Encourages off‑by‑one errors and invalid states; unclear invariants.  
**Fix:** Model `Slot` objects with a **State** pattern (`Vacant`/`Occupied`, later `Reserved`/`Charging`). Keep explicit `vehicle: Optional[Vehicle]`.  
**Test idea:** State transition tests (invalid transitions raise; valid ones pass).

---

## 7) Duplicated search logic for EV vs non‑EV (**maintainability**)
**Files/Lines:** `src/ParkingManager.py` (multiple `getSlotNumFromX*` across EV & non‑EV)  
**Why it’s a problem:** Two sets of nearly identical code drift apart; higher bug risk (see #2).  
**Fix:** Create a `ParkingRepository.find(criteria)` that unifies lookup over all slots with optional filters (fuel, kind, color, make, model).  
**Test idea:** Parametrized tests over criteria with a seeded lot.

---

## 8) Ambiguous naming / inconsistent `getType()` (**clarity**)
**Files/Lines:** `src/Vehicle.py`, `src/ElectricVehicle.py`  
**Why it’s a problem:** EV “bike” returns `"Motorcycle"`; EV “car” returns `"Car"`, EV-ness is implicit only by subclass.  
**Fix:** Introduce `VehicleKind = {CAR, MOTORCYCLE, BUS}` and `FuelType = {ICE, EV}` (enums). All vehicles expose `kind` and `fuel`.  
**Test idea:** Assert `kind`/`fuel` for each subclass; factory assigns them consistently.

---

## 9) Module‑level GUI bootstrap / side effects on import (**testability**)
**Files/Lines:** `src/ParkingManager.py` (Tk app created at import)  
**Why it’s a problem:** Importing the module during tests may try to create windows; fails in headless CI.  
**Fix:** Move UI bootstrap under `if __name__ == "__main__":` or a `main()` entrypoint.  
**Test idea:** `import ParkingManager` should not open a window; running `python ParkingManager.py` should.

---

## 10) Domain writes directly to UI controls (**design smell**)
**Files/Lines:** `src/ParkingManager.py` (`status()` inserts into a `Text` widget)  
**Why it’s a problem:** Violates separation of concerns; formatting and logic tangled.  
**Fix:** Have domain return status strings/DTOs; the GUI is responsible for rendering.  
**Test idea:** Assert returned status text for known operations (park, leave, not found).

---

## 11) Hard‑coded window geometry & constants (**cosmetic/UX**)
**Files/Lines:** `src/ParkingManager.py` (fixed geometry in code)  
**Why it’s a problem:** Limits adaptability; complicates headless modes.  
**Fix:** Move to a config/constants file; allow resize or test flag.  
**Test idea:** N/A (non‑functional).

---

## 12) Missing type hints (**hygiene**)
**Files/Lines:** All modules  
**Why it’s a problem:** Static analysis can’t help; makes bugs like #2 easier to miss.  
**Fix:** Add type hints to public functions and data structures (start with `ParkingLot`, factory, and repository).  
**Test idea:** `mypy src` shows fewer warnings; CI enforces.

---

# Mapping to planned refactors & patterns
- **Factory Pattern** → fixes #4, supports #8, reduces duplication in creation code.  
- **State Pattern (Slot lifecycle)** → fixes #6, simplifies #3, enables clearer `park/leave` invariants.  
- **Repository (optional)** → addresses #7 and improves query cohesion.  
- **UI/Domain split** → #5, #9, #10 (introduce `ParkingService`, return DTOs).
