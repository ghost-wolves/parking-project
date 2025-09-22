from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, TypedDict

from slot import Slot
from vehicle_factory import create as create_vehicle

Fuel = Literal["ICE", "EV"]
Kind = Literal["CAR", "MOTORCYCLE", "BUS", "TRUCK"]


@dataclass(frozen=True)
class VehicleSpec:
    """Specification used to construct a vehicle through the factory."""
    regnum: str
    make: str
    model: str
    color: str
    fuel: Fuel
    kind: Kind


class ParkResult(TypedDict):
    ok: bool
    message: str
    slot_ui: int | None  # 1-based index for UI


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
    Pure application layer for the Parking Lot.
    - Uses Slot state objects (no '-1' sentinels).
    - Vehicle construction is centralized via vehicle_factory.
    - Slot IDs are normalized: 0-based internally, 1-based for UI/messages.
    - Temporary API shim: leave(..., fuel="ICE") remains for back-compat and
      should be made required after the Factory/State milestones.
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
        self.slots: list[Slot] = [Slot(i, level, "ICE") for i in range(capacity)]
        self.evSlots: list[Slot] = [Slot(i, level, "EV") for i in range(ev_capacity)]


    # ---------- helpers ----------
    @staticmethod
    def _to_ui(idx: int) -> int:
        """Convert internal 0-based index to 1-based UI slot number."""
        return idx + 1

    @staticmethod
    def _from_ui(slot_ui: int) -> int | None:
        """Convert 1-based UI slot number to internal 0-based index (validated)."""
        if slot_ui <= 0:
            return None
        return slot_ui - 1

    def _get_empty_slot(self) -> int | None:
        """Return first vacant ICE slot index, else None."""
        for i, s in enumerate(self.slots):
            if s.is_vacant:
                return i
        return None

    def _get_empty_ev_slot(self) -> int | None:
        """Return first vacant EV slot index, else None."""
        for i, s in enumerate(self.evSlots):
            if s.is_vacant:
                return i
        return None

    # ---------- API ----------
    def park(self, spec: VehicleSpec) -> ParkResult:
        """Park a vehicle. Returns ok/message and 1-based slot if successful."""
        # minimal sanitize: trim strings so lookups behave predictably
        spec = VehicleSpec(
            regnum=spec.regnum.strip(),
            make=spec.make.strip(),
            model=spec.model.strip(),
            color=spec.color.strip(),
            fuel=spec.fuel,
            kind=spec.kind,
        )
        if not spec.regnum:
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
        """
        Free a slot by its 1-based UI number.
        NOTE: 'fuel' is temporarily optional for back-compat; pass explicitly where possible.
        """
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
        """Tabular rows for ICE vehicles currently parked."""
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
        """Tabular rows for EV vehicles currently parked."""
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

    def ev_charge_rows(self) -> list[dict[str, Any]]:
        """Rows for EV charge status (slot, level, reg, charge%)."""
        rows: list[dict[str, Any]] = []
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
        """Return 1-based EV slot numbers where vehicle.make == make."""
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
        """Return 1-based EV slot numbers where vehicle.model == model."""
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
        """Return 1-based ICE slot numbers where vehicle.make == make."""
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
        """Return 1-based ICE slot numbers where vehicle.model == model."""
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
        """Return 1-based slot numbers (ICE+EV) where vehicle.color == color."""
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
        """Return registration numbers (ICE+EV) where vehicle.color == color."""
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
        # --- Registration finders (ICE + EV) ---
    def all_slots_by_reg(self, regnum: str) -> list[int]:
        """Return 1-based slot numbers for any vehicle whose regnum matches (ICE+EV)."""
        out: list[int] = []
        r = (regnum or "").strip()
        if not r:
            return out
        for i, s in enumerate(self.slots):
            v = s.vehicle
            if v is not None and str(v.regnum) == r:
                out.append(self._to_ui(i))
        for i, s in enumerate(self.evSlots):
            v = s.vehicle
            if v is not None and str(v.regnum) == r:
                out.append(self._to_ui(i))
        return out

    def first_slot_by_reg(self, regnum: str) -> int | None:
        """Return the first matching 1-based slot number, or None."""
        slots = self.all_slots_by_reg(regnum)
        return slots[0] if slots else None

    # --- Persistence / Export ---

    def to_dict(self) -> dict:
        """Serialize lot state to a plain dict (JSON-safe)."""
        def veh2d(v):
            if v is None:
                return None
            # Determine fuel by presence of 'charge' attribute (EV) vs not (ICE)
            fuel = "EV" if hasattr(v, "charge") else "ICE"
            # Map concrete class to kind
            cls = v.__class__.__name__
            if fuel == "EV":
                kind = "CAR" if "Car" in cls else "MOTORCYCLE"
            else:
                if "Truck" in cls:
                    kind = "TRUCK"
                elif "Bus" in cls:
                    kind = "BUS"
                elif "Motorcycle" in cls:
                    kind = "MOTORCYCLE"
                else:
                    kind = "CAR"
            out = {
                "regnum": v.regnum,
                "make": v.make,
                "model": v.model,
                "color": v.color,
                "fuel": fuel,
                "kind": kind,
            }
            if fuel == "EV":
                out["charge"] = getattr(v, "charge", 0)
            return out

        return {
            "level": self.level,
            "capacity": self.capacity,
            "ev_capacity": self.ev_capacity,
            "slots": [veh2d(s.vehicle) for s in self.slots],
            "evSlots": [veh2d(s.vehicle) for s in self.evSlots],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ParkingService":
        """Construct a ParkingService from a dict produced by to_dict()."""
        svc = cls(
            capacity=int(data.get("capacity", 0)),
            ev_capacity=int(data.get("ev_capacity", 0)),
            level=int(data.get("level", 1)),
        )
        # Recreate vehicles via factory and occupy slots in order
        from vehicle_factory import create as create_vehicle  # local import to avoid cycles
        for i, v in enumerate(data.get("slots", [])):
            if v:
                entity = create_vehicle(
                    v["regnum"], v["make"], v["model"], v["color"], v["fuel"], v["kind"]
                )
                svc.slots[i].occupy(entity)
        for i, v in enumerate(data.get("evSlots", [])):
            if v:
                entity = create_vehicle(
                    v["regnum"], v["make"], v["model"], v["color"], v["fuel"], v["kind"]
                )
                # Preserve EV charge if present
                if "charge" in v:
                    setattr(entity, "charge", int(v["charge"]))
                svc.evSlots[i].occupy(entity)
        return svc

    def save_json(self, path: str) -> None:
        """Write the current lot to a JSON file."""
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_json(cls, path: str) -> "ParkingService":
        """Read a lot from a JSON file and return a fresh service instance."""
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_csv_rows(self, include_ev: bool = True) -> list[list[str]]:
        """
        Return a combined CSV-like table:
        header + rows of ICE (then EV if include_ev=True).
        """
        header = ["slot_ui", "level", "regnum", "color", "make", "model", "fuel"]
        rows: list[list[str]] = [header]
        for r in self.status_rows():
            rows.append([
                str(r["slot_ui"]), str(r["level"]), r["regnum"],
                r["color"], r["make"], r["model"], "ICE",
            ])
        if include_ev:
            for r in self.ev_status_rows():
                rows.append([
                    str(r["slot_ui"]), str(r["level"]), r["regnum"],
                    r["color"], r["make"], r["model"], "EV",
                ])
        return rows

    def save_csv(self, path: str, include_ev: bool = True) -> None:
        """Write a combined status CSV to disk."""
        import csv
        rows = self.to_csv_rows(include_ev=include_ev)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

