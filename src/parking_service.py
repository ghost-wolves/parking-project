# src/parking_service.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal, TypedDict, List

import Vehicle
import ElectricVehicle
from vehicle_factory import create as create_vehicle
from slot import Slot

Fuel = Literal["ICE", "EV"]
Kind = Literal["CAR", "MOTORCYCLE", "BUS", "TRUCK"]

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
    slot_ui: Optional[int]

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
    Pure application layer with Slot state model.
    - Internal truth: list[Slot] for ICE and EV (no more -1 sentinels).
    - UI-facing numbers are 1-based via _to_ui/_from_ui.
    - Vehicle construction centralized in vehicle_factory.
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

        # State-model slots
        self.slots: List[Slot]   = [Slot(i, level, "ICE") for i in range(capacity)]
        self.evSlots: List[Slot] = [Slot(i, level, "EV")  for i in range(ev_capacity)]

    # ---------- helpers ----------
    @staticmethod
    def _to_ui(idx: int) -> int:
        return idx + 1

    @staticmethod
    def _from_ui(slot_ui: int) -> Optional[int]:
        if slot_ui <= 0:
            return None
        return slot_ui - 1

    def _get_empty_slot(self) -> Optional[int]:
        for i, s in enumerate(self.slots):
            if s.is_vacant:
                return i
        return None

    def _get_empty_ev_slot(self) -> Optional[int]:
        for i, s in enumerate(self.evSlots):
            if s.is_vacant:
                return i
        return None

    # ---------- API ----------
    def park(self, spec: VehicleSpec) -> ParkResult:
        if not spec.regnum.strip():
            return {"ok": False, "message": "registration required", "slot_ui": None}

        if spec.fuel == "EV":
            idx = self._get_empty_ev_slot()
            if idx is None:
                return {"ok": False, "message": "Sorry, EV lot is full", "slot_ui": None}
            entity = create_vehicle(spec.regnum, spec.make, spec.model, spec.color, spec.fuel, spec.kind)
            self.evSlots[idx].occupy(entity)
            ui = self._to_ui(idx)
            return {"ok": True, "message": f"Allocated EV slot number: {ui}", "slot_ui": ui}

        # ICE
        idx = self._get_empty_slot()
        if idx is None:
            return {"ok": False, "message": "Sorry, parking lot is full", "slot_ui": None}
        entity = create_vehicle(spec.regnum, spec.make, spec.model, spec.color, spec.fuel, spec.kind)
        self.slots[idx].occupy(entity)
        ui = self._to_ui(idx)
        return {"ok": True, "message": f"Allocated slot number: {ui}", "slot_ui": ui}

    def leave(self, slot_ui: int, fuel: Fuel = "ICE") -> LeaveResult:
        idx = self._from_ui(slot_ui)
        if idx is None:
            return {"ok": False, "message": "slot must be >= 1"}

        if fuel == "EV":
            if 0 <= idx < len(self.evSlots) and not self.evSlots[idx].is_vacant:
                self.evSlots[idx].free()
                return {"ok": True, "message": f"EV slot {slot_ui} is free"}
            return {"ok": False, "message": "Slot empty or invalid"}

        # ICE
        if 0 <= idx < len(self.slots) and not self.slots[idx].is_vacant:
            self.slots[idx].free()
            return {"ok": True, "message": f"Slot {slot_ui} is free"}
        return {"ok": False, "message": "Slot empty or invalid"}

    # ---------- Reporting ----------
    def status_rows(self) -> list[StatusRow]:
        rows: list[StatusRow] = []
        for i, s in enumerate(self.slots):
            v = s.vehicle
            if v is not None:
                rows.append(
                    {
                        "slot_ui": self._to_ui(i),
                        "level": s.level,
                        "regnum": v.regnum,
                        "color": v.color,
                        "make": v.make,
                        "model": v.model,
                    }
                )
        return rows

    def ev_status_rows(self) -> list[StatusRow]:
        rows: list[StatusRow] = []
        for i, s in enumerate(self.evSlots):
            v = s.vehicle
            if v is not None:
                rows.append(
                    {
                        "slot_ui": self._to_ui(i),
                        "level": s.level,
                        "regnum": v.regnum,
                        "color": v.color,
                        "make": v.make,
                        "model": v.model,
                    }
                )
        return rows

    def ev_charge_rows(self) -> list[dict]:
        rows: list[dict] = []
        for i, s in enumerate(self.evSlots):
            v = s.vehicle
            if v is not None:
                rows.append(
                    {
                        "slot_ui": self._to_ui(i),
                        "level": s.level,
                        "regnum": v.regnum,
                        "charge": v.charge,
                    }
                )
        return rows

    # ---------- Finders ----------
    def ev_slots_by_make(self, make: str) -> list[int]:
        out: list[int] = []
        m = (make or "").strip()
        if not m:
            return out
        for i, s in enumerate(self.evSlots):
            v = s.vehicle
            if v is not None and str(v.make) == m:
                out.append(self._to_ui(i))
        return out

    def ev_slots_by_model(self, model: str) -> list[int]:
        out: list[int] = []
        md = (model or "").strip()
        if not md:
            return out
        for i, s in enumerate(self.evSlots):
            v = s.vehicle
            if v is not None and str(v.model) == md:
                out.append(self._to_ui(i))
        return out

    def slots_by_make(self, make: str) -> list[int]:
        out: list[int] = []
        m = (make or "").strip()
        if not m:
            return out
        for i, s in enumerate(self.slots):
            v = s.vehicle
            if v is not None and str(v.make) == m:
                out.append(self._to_ui(i))
        return out

    def slots_by_model(self, model: str) -> list[int]:
        out: list[int] = []
        md = (model or "").strip()
        if not md:
            return out
        for i, s in enumerate(self.slots):
            v = s.vehicle
            if v is not None and str(v.model) == md:
                out.append(self._to_ui(i))
        return out

    def all_slots_by_color(self, color: str) -> list[int]:
        out: list[int] = []
        c = (color or "").strip()
        if not c:
            return out
        for i, s in enumerate(self.slots):
            v = s.vehicle
            if v is not None and str(v.color) == c:
                out.append(self._to_ui(i))
        for i, s in enumerate(self.evSlots):
            v = s.vehicle
            if v is not None and str(v.color) == c:
                out.append(self._to_ui(i))
        return out

    def all_regnums_by_color(self, color: str) -> list[str]:
        regs: list[str] = []
        c = (color or "").strip()
        if not c:
            return regs
        for s in self.slots:
            v = s.vehicle
            if v is not None and str(v.color) == c:
                regs.append(str(v.regnum))
        for s in self.evSlots:
            v = s.vehicle
            if v is not None and str(v.color) == c:
                regs.append(str(v.regnum))
        return regs
