import importlib
import pytest # type: ignore

def import_src(mod: str):
    return importlib.import_module(mod)

def test_ev_subclass_relationship_fixed():
    EV = import_src("ElectricVehicle")
    ecar = EV.ElectricCar("ABC123", "Tesla", "Model 3", "Blue")
    ebike = EV.ElectricBike("MOTO1", "Zero", "FXE", "Black")
    assert isinstance(ecar, EV.ElectricVehicle)
    assert isinstance(ebike, EV.ElectricVehicle)

from src.parking_service import ParkingService, VehicleSpec

def test_ev_finders_by_make_and_model():
    svc = ParkingService(capacity=0, ev_capacity=3, level=1)
    # Seed two EVs
    r1 = svc.park(VehicleSpec("E1", "Tesla", "Model 3", "Blue", fuel="EV", kind="CAR"))
    r2 = svc.park(VehicleSpec("E2", "Nissan","Leaf","Green", fuel="EV", kind="CAR"))
    assert r1["ok"] and r2["ok"]

    # Make-based lookup
    assert svc.ev_slots_by_make("Tesla") == [1]
    assert svc.ev_slots_by_make("Nissan") == [2]
    assert svc.ev_slots_by_make("Ford") == []

    # Model-based lookup
    assert svc.ev_slots_by_model("Model 3") == [1]
    assert svc.ev_slots_by_model("Leaf") == [2]
    assert svc.ev_slots_by_model("Bolt") == []

