# tests/test_smoke.py
import importlib


def test_imports():
    for mod in ("Vehicle", "ElectricVehicle", "ParkingManager"):
        importlib.import_module(mod)
