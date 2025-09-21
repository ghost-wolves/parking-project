# src/slot.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal, Any

Fuel = Literal["ICE", "EV"]

@dataclass
class Slot:
    """Single parking slot with simple state (VACANT/OCCUPIED)."""
    index: int          # 0-based internal index
    level: int          # floor number
    fuel: Fuel          # which pool this slot belongs to
    vehicle: Optional[Any] = None  # holds concrete Vehicle/ElectricVehicle

    @property
    def is_vacant(self) -> bool:
        return self.vehicle is None

    def occupy(self, vehicle: Any) -> None:
        if not self.is_vacant:
            raise ValueError(f"Slot {self.index+1} ({self.fuel}) already occupied")
        self.vehicle = vehicle

    def free(self) -> None:
        if self.is_vacant:
            raise ValueError(f"Slot {self.index+1} ({self.fuel}) is already vacant")
        self.vehicle = None
