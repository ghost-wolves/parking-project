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
    PURE application layer: owns the parking state and returns data (no tkinter).
    Step 8 keeps the baseline logic (including sentinels & counters) so behavior
    stays familiar. We’ll improve with Factory/State in Steps 12–15.
    """

    # -------- lifecycle --------
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

        # Baseline representation (kept for now)
        self.slots: List[Union[int, Vehicle.Vehicle]] = [-1] * capacity
        self.evSlots: List[Union[int, ElectricVehicle.ElectricVehicle]] = [-1] * ev_capacity

        self.slotid = 0     # baseline's user-facing counter for ICE
        self.slotEvId = 0   # baseline's user-facing counter for EV
        self.numOfOccupiedSlots = 0
        self.numOfOccupiedEvSlots = 0

    # -------- helpers (baseline style) --------
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

    # -------- API --------
    def park(self, spec: VehicleSpec) -> ParkResult:
        if not spec.regnum.strip():
            return {"ok": False, "message": "registration required", "slot_ui": None}

        is_ev = spec.fuel == "EV"
        is_motor = spec.kind == "MOTORCYCLE"

        # Keep baseline counters/behavior for now
        if is_ev:
            if self.numOfOccupiedEvSlots >= self.ev_capacity:
                return {"ok": False, "message": "Sorry, EV lot is full", "slot_ui": None}
            idx = self._get_empty_ev_slot()
            if idx is None:
                return {"ok": False, "message": "Sorry, EV lot is full", "slot_ui": None}
            # Baseline EV class selection (we’ll centralize later with a Factory)
            if is_motor:
                self.evSlots[idx] = ElectricVehicle.ElectricBike(
                    spec.regnum, spec.make, spec.model, spec.color
                )
            else:
                self.evSlots[idx] = ElectricVehicle.ElectricCar(
                    spec.regnum, spec.make, spec.model, spec.color
                )
            self.slotEvId += 1
            self.numOfOccupiedEvSlots += 1
            # Baseline returns a separate counter (not the array index)
            return {
                "ok": True,
                "message": f"Allocated EV slot number: {self.slotEvId}",
                "slot_ui": self.slotEvId,
            }
        else:
            if self.numOfOccupiedSlots >= self.capacity:
                return {"ok": False, "message": "Sorry, parking lot is full", "slot_ui": None}
            idx = self._get_empty_slot()
            if idx is None:
                return {"ok": False, "message": "Sorry, parking lot is full", "slot_ui": None}
            # Baseline ICE class selection (note: mix-ups exist in original; we’ll fix later)
            if is_motor:
                self.slots[idx] = Vehicle.Motorcycle(spec.regnum, spec.make, spec.model, spec.color)
            elif spec.kind == "TRUCK":
                self.slots[idx] = Vehicle.Truck(spec.regnum, spec.make, spec.model, spec.color)
            elif spec.kind == "BUS":
                self.slots[idx] = Vehicle.Bus(spec.regnum, spec.make, spec.model, spec.color)
            else:
                self.slots[idx] = Vehicle.Car(spec.regnum, spec.make, spec.model, spec.color)
            self.slotid += 1
            self.numOfOccupiedSlots += 1
            return {"ok": True, "message": f"Allocated slot number: {self.slotid}", "slot_ui": self.slotid}

    def leave(self, slot_ui: int, fuel: Fuel = "ICE") -> LeaveResult:
        if slot_ui <= 0:
            return {"ok": False, "message": "slot must be >= 1"}
        if fuel == "EV":
            if self.numOfOccupiedEvSlots == 0:
                return {"ok": False, "message": "No EV vehicles to remove"}
            # Baseline: interprets UI slot as 1-based into array
            idx = slot_ui - 1
            if 0 <= idx < len(self.evSlots) and self.evSlots[idx] != -1:
                self.evSlots[idx] = -1
                self.numOfOccupiedEvSlots -= 1
                return {"ok": True, "message": f"EV slot {slot_ui} is free"}
            return {"ok": False, "message": "Slot empty or invalid"}
        else:
            if self.numOfOccupiedSlots == 0:
                return {"ok": False, "message": "No vehicles to remove"}
            idx = slot_ui - 1
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
                        "slot_ui": i + 1,
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
                        "slot_ui": i + 1,
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
                rows.append({"slot_ui": i + 1, "level": self.level, "regnum": v.regnum, "charge": v.charge})
        return rows
