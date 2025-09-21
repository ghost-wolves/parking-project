import importlib
import pytest

def import_src(mod: str):
    return importlib.import_module(mod)

def test_import_vehicle_modules():
    import_src("Vehicle")
    import_src("ElectricVehicle")

@pytest.mark.xfail(reason="Baseline defect: EV subclasses don't inherit ElectricVehicle", strict=True)
def test_ev_subclass_relationship_is_broken_baseline():
    EV = import_src("ElectricVehicle")
    ecar = EV.ElectricCar("ABC123", "Tesla", "Model 3", "Blue")   # 4 args
    ebike = EV.ElectricBike("MOTO1", "Zero", "FXE", "Black")      # 4 args
    assert isinstance(ecar, EV.ElectricVehicle)
    assert isinstance(ebike, EV.ElectricVehicle)

def test_ev_classes_construct_and_expose_fields():
    EV = import_src("ElectricVehicle")
    ecar = EV.ElectricCar("ABC123", "Tesla", "Model 3", "Blue")   # 4 args
    # baseline: charge defaults to 0
    assert hasattr(ecar, "registration") or hasattr(ecar, "regnum")
    # Normalize field name check (code uses regnum, not registration)
    assert hasattr(ecar, "regnum")
    assert hasattr(ecar, "make")
    assert hasattr(ecar, "model")
    assert hasattr(ecar, "color")
    assert hasattr(ecar, "charge")
