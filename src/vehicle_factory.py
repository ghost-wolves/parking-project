# src/vehicle_factory.py
from __future__ import annotations
from typing import Literal

import Vehicle
import ElectricVehicle

Fuel = Literal["ICE", "EV"]
Kind = Literal["CAR", "MOTORCYCLE", "BUS", "TRUCK"]


def create(
    regnum: str,
    make: str,
    model: str,
    color: str,
    fuel: Fuel,
    kind: Kind,
):
    """
    Construct the correct concrete Vehicle based on fuel/kind.
    Raises ValueError for unsupported combos (e.g., EV + BUS/TRUCK).
    """
    if fuel == "EV":
        if kind == "CAR":
            return ElectricVehicle.ElectricCar(regnum, make, model, color)
        if kind == "MOTORCYCLE":
            return ElectricVehicle.ElectricBike(regnum, make, model, color)
        raise ValueError("Unsupported EV kind (only CAR or MOTORCYCLE are allowed for EV)")
    # ICE
    if kind == "MOTORCYCLE":
        return Vehicle.Motorcycle(regnum, make, model, color)
    if kind == "TRUCK":
        return Vehicle.Truck(regnum, make, model, color)
    if kind == "BUS":
        return Vehicle.Bus(regnum, make, model, color)
    return Vehicle.Car(regnum, make, model, color)
