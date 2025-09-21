# src/Vehicle.py
from __future__ import annotations


class Vehicle:
    def __init__(self, regnum: str, make: str, model: str, color: str) -> None:
        self.regnum: str = regnum
        self.make: str = make
        self.model: str = model
        self.color: str = color

    def getType(self) -> str:
        return "Vehicle"


class Car(Vehicle):
    def __init__(self, regnum: str, make: str, model: str, color: str) -> None:
        super().__init__(regnum, make, model, color)

    def getType(self) -> str:
        return "Car"


class Truck(Vehicle):
    def __init__(self, regnum: str, make: str, model: str, color: str) -> None:
        super().__init__(regnum, make, model, color)

    def getType(self) -> str:
        return "Truck"


class Bus(Vehicle):
    def __init__(self, regnum: str, make: str, model: str, color: str) -> None:
        super().__init__(regnum, make, model, color)

    def getType(self) -> str:
        return "Bus"


class Motorcycle(Vehicle):
    def __init__(self, regnum: str, make: str, model: str, color: str) -> None:
        super().__init__(regnum, make, model, color)

    def getType(self) -> str:
        return "Motorcycle"
