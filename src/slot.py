from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Fuel = Literal["ICE", "EV"]

@dataclass
class Slot:
    """Single parking slot with simple state (VACANT/OCCUPIED)."""
    index: int          # 0-based internal index
    level: int          # floor number
    fuel: Fuel          # which pool this slot belongs to
    vehicle: Any | None = None  # concrete Vehicle/ElectricVehicle

    @property
    def is_vacant(self) -> bool:
        """True if the slot currently has no vehicle."""
        return self.vehicle is None

    def occupy(self, vehicle: Any) -> None:
        """Place a vehicle into this slot; raises if already occupied."""
        if not self.is_vacant:
            raise ValueError(f"Slot {self.index+1} ({self.fuel}) already occupied")
        self.vehicle = vehicle

    def free(self) -> None:
        """Free this slot; raises if already vacant."""
        if self.is_vacant:
            raise ValueError(f"Slot {self.index+1} ({self.fuel}) is already vacant")
        self.vehicle = None
