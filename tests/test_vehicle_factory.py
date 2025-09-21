import pytest # type: ignore
from src.vehicle_factory import create
import importlib

EV = importlib.import_module("ElectricVehicle")
V = importlib.import_module("Vehicle")

@pytest.mark.parametrize(
    "fuel,kind,expected",
    [
        ("ICE", "CAR", V.Car),
        ("ICE", "MOTORCYCLE", V.Motorcycle),
        ("ICE", "BUS", V.Bus),
        ("ICE", "TRUCK", V.Truck),
        ("EV", "CAR", EV.ElectricCar),
        ("EV", "MOTORCYCLE", EV.ElectricBike),
    ],
)
def test_factory_returns_correct_class(fuel, kind, expected):
    obj = create("R1", "Make", "Model", "Red", fuel, kind)
    assert isinstance(obj, expected)

def test_factory_rejects_unsupported_ev_kind():
    with pytest.raises(ValueError):
        create("R1", "Make", "Model", "Red", "EV", "BUS")
    with pytest.raises(ValueError):
        create("R1", "Make", "Model", "Red", "EV", "TRUCK")
