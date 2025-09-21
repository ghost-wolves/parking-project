# src/ElectricVehicle.py
from __future__ import annotations


class ElectricVehicle:
    def __init__(self, regnum: str, make: str, model: str, color: str) -> None:
        self.regnum: str = regnum
        self.make: str = make
        self.model: str = model
        self.color: str = color
        self.charge: int = 0

    def getType(self) -> str:
        return "ElectricVehicle"


class ElectricCar(ElectricVehicle):
    def __init__(self, regnum: str, make: str, model: str, color: str) -> None:
        super().__init__(regnum, make, model, color)

    def getType(self) -> str:
        return "Car"


class ElectricBike(ElectricVehicle):
    def __init__(self, regnum: str, make: str, model: str, color: str) -> None:
        super().__init__(regnum, make, model, color)

    def getType(self) -> str:
        return "Motorcycle"
