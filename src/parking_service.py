# src/parking_service.py
from dataclasses import dataclass
from typing import Optional, Literal, TypedDict


Fuel = Literal["ICE", "EV"]
Kind = Literal["CAR", "MOTORCYCLE", "BUS", "TRUCK"]  # matches current classes


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
    slot_ui: Optional[int]  # 1-based for UI if available


class LeaveResult(TypedDict):
    ok: bool
    message: str


class ParkingService:
    """
    Thin application façade for parking operations.
    Step 7: keep it PURE (no tkinter), validate inputs,
    and set up the signatures we’ll fill in during Steps 8–15.
    """

    def __init__(self, capacity: int, ev_capacity: int, level: int = 1) -> None:
        if capacity < 0 or ev_capacity < 0:
            raise ValueError("capacities must be >= 0")
        if capacity == 0 and ev_capacity == 0:
            raise ValueError("at least one of capacity or ev_capacity must be > 0")
        if level <= 0:
            raise ValueError("level must be >= 1")

        # For Step 7 we simply record sizes. In Step 8, we will
        # wire this to the existing ParkingLot and stop Tk usage.
        self.capacity = capacity
        self.ev_capacity = ev_capacity
        self.level = level

    # ---- API we’ll flesh out in Step 8+ ----

    def park(self, spec: VehicleSpec) -> ParkResult:
        # Step 7: just validate & stub; Step 8 will hook to domain
        if not spec.regnum.strip():
            return {"ok": False, "message": "registration required", "slot_ui": None}
        return {"ok": False, "message": "not implemented (Step 8)", "slot_ui": None}

    def leave(self, slot_ui: int) -> LeaveResult:
        if slot_ui <= 0:
            return {"ok": False, "message": "slot must be >= 1"}
        return {"ok": False, "message": "not implemented (Step 8)"}
