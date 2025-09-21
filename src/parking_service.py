# src/parking_service.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal, TypedDict, List, Union

import Vehicle
import ElectricVehicle

Fuel = Literal["ICE", "EV"]
Kind = Literal["CAR", "MOTORCYCLE", "BUS", "TRUCK"]  # mirrors current classes


@dataclass(frozen=True)
class VehicleSpec:
    regnum: str
    make: str
    model: str
    color: str
    fuel: Fuel
    kind: Kind


class ParkResult(TypedDict):
    ok: bool
    message: str
    slot_ui: Optional[int]  # 1-based index for UI


class LeaveResult(TypedDict):
    ok: bool
    message: str


class StatusRow(TypedDict):
    slot_ui: int
    level: int
    regnum: str
    color: str
    make: str
    model: str


class ParkingService:
    """
    Step 8–10: Pure application layer with slot ID normalization.

    - Pure Python: no tkinter, returns data structures.
    - Single source of truth for slot IDs = array index (0-based).
    - UI-facing numbers are 1-based via helpers _to_ui/_from_ui.
    - Temporary API shim: leave(..., fuel="ICE") keeps old callers working.
      (We’ll require explicit fuel after the Factory/State refactor.)
    """

    def __init__(self, capacity: int, ev_capacity: int, level: int = 1) -> None:
        if capacity < 0 or ev_capacity < 0:
            raise ValueError("capacities must be >= 0")
        if capacity == 0 and ev_capacity == 0:
            raise ValueError("at least one of capacity or ev_capacity must be > 0")
        if level <= 0:
            raise ValueError("level must be >= 1")

        self.level = level
        self.capacity = capacity
        self.ev_capacity = ev_capacity

        # Internal representation (kept baseline structures for now)
        self.slots: List[Union[int, Vehicle.Vehicle]] = [-1] * capacity
        self.evSlots: List[Union[int, ElectricVehicle.ElectricVehicle]] = [-1] * ev_capacity

        # Removed separate user-facing counters; we use indices
        self.numOfOccupiedSlots = 0
        self.numOfOccupiedEvSlots = 0

    # ---------- helpers ----------
    @staticmethod
    def _to_ui(idx: int) -> int:
        """Convert internal 0-based index to 1-based UI slot number."""
        return idx + 1

    @staticmethod
    def _from_ui(slot_ui: int) -> Optional[int]:
        """Convert 1-based UI slot number to internal 0-based index."""
        if slot_ui <= 0:
            return None
        return slot_ui - 1

    def _get_empty_slot(self) -> Optional[int]:
        for i, v in enumerate(self.slots):
            if v == -1:
                return i
        return None

    def _get_empty_ev_slot(self) -> Optional[int]:
        for i, v in enumerate(self.evSlots):
            if v == -1:
                return i
        return None

    # ---------- API ----------
    def park(self, spec: VehicleSpec) -> ParkResult:
        if not spec.regnum.strip():
            return {"ok": False, "message": "registration required", "slot_ui": None}

        is_ev = spec.fuel == "EV"
        is_motor = spec.kind == "MOTORCYCLE"

        if is_ev:
            if self.numOfOccupiedEvSlots >= self.ev_capacity:
                return {"ok": False, "message": "Sorry, EV lot is full", "slot_ui": None}
            idx = self._get_empty_ev_slot()
            if idx is None:
                return {"ok": False, "message": "Sorry, EV lot is full", "slot_ui": None}

            self.evSlots[idx] = (
                ElectricVehicle.ElectricBike(spec.regnum, spec.make, spec.model, spec.color)
                if is_motor
                else ElectricVehicle.ElectricCar(spec.regnum, spec.make, spec.model, spec.color)
            )
            self.numOfOccupiedEvSlots += 1
            ui = self._to_ui(idx)
            return {"ok": True, "message": f"Allocated EV slot number: {ui}", "slot_ui": ui}

        # ICE
        if self.numOfOccupiedSlots >= self.capacity:
            return {"ok": False, "message": "Sorry, parking lot is full", "slot_ui": None}
        idx = self._get_empty_slot()
        if idx is None:
            return {"ok": False, "message": "Sorry, parking lot is full", "slot_ui": None}

        if is_motor:
            self.slots[idx] = Vehicle.Motorcycle(spec.regnum, spec.make, spec.model, spec.color)
        elif spec.kind == "TRUCK":
            self.slots[idx] = Vehicle.Truck(spec.regnum, spec.make, spec.model, spec.color)
        elif spec.kind == "BUS":
            self.slots[idx] = Vehicle.Bus(spec.regnum, spec.make, spec.model, spec.color)
        else:
            self.slots[idx] = Vehicle.Car(spec.regnum, spec.make, spec.model, spec.color)

        self.numOfOccupiedSlots += 1
        ui = self._to_ui(idx)
        return {"ok": True, "message": f"Allocated slot number: {ui}", "slot_ui": ui}

    def leave(self, slot_ui: int, fuel: Fuel = "ICE") -> LeaveResult:
        idx = self._from_ui(slot_ui)
        if idx is None:
            return {"ok": False, "message": "slot must be >= 1"}

        if fuel == "EV":
            # Check the requested slot first
            if 0 <= idx < len(self.evSlots) and self.evSlots[idx] != -1:
                self.evSlots[idx] = -1
                self.numOfOccupiedEvSlots -= 1
                return {"ok": True, "message": f"EV slot {slot_ui} is free"}
            # If nothing there, choose a precise error over generic count checks
            return {"ok": False, "message": "Slot empty or invalid"}

        # ICE
        if 0 <= idx < len(self.slots) and self.slots[idx] != -1:
            self.slots[idx] = -1
            self.numOfOccupiedSlots -= 1
            return {"ok": True, "message": f"Slot {slot_ui} is free"}
        return {"ok": False, "message": "Slot empty or invalid"}


    def status_rows(self) -> list[StatusRow]:
        rows: list[StatusRow] = []
        for i, v in enumerate(self.slots):
            if v != -1:
                rows.append(
                    {
                        "slot_ui": self._to_ui(i),
                        "level": self.level,
                        "regnum": v.regnum,
                        "color": v.color,
                        "make": v.make,
                        "model": v.model,
                    }
                )
        return rows

    def ev_status_rows(self) -> list[StatusRow]:
        rows: list[StatusRow] = []
        for i, v in enumerate(self.evSlots):
            if v != -1:
                rows.append(
                    {
                        "slot_ui": self._to_ui(i),
                        "level": self.level,
                        "regnum": v.regnum,
                        "color": v.color,
                        "make": v.make,
                        "model": v.model,
                    }
                )
        return rows

    def ev_charge_rows(self) -> list[dict]:
        rows: list[dict] = []
        for i, v in enumerate(self.evSlots):
            if v != -1:
                rows.append(
                    {
                        "slot_ui": self._to_ui(i),
                        "level": self.level,
                        "regnum": v.regnum,
                        "charge": v.charge,
                    }
                )
        return rows

        # -------- EV finders (fixed) --------
    def ev_slots_by_make(self, make: str) -> list[int]:
        """Return 1-based UI slot numbers for EVs that match the given make."""
        out: list[int] = []
        m = (make or "").strip()
        if not m:
            return out
        for i, v in enumerate(self.evSlots):
            if v != -1 and str(v.make) == m:
                out.append(self._to_ui(i))
        return out

    def ev_slots_by_model(self, model: str) -> list[int]:
        """Return 1-based UI slot numbers for EVs that match the given model."""
        out: list[int] = []
        md = (model or "").strip()
        if not md:
            return out
        for i, v in enumerate(self.evSlots):
            if v != -1 and str(v.model) == md:
                out.append(self._to_ui(i))
        return out
