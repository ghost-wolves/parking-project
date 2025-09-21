import importlib
import pytest

def import_src(mod: str):
    return importlib.import_module(mod)

def test_ev_subclass_relationship_fixed():
    EV = import_src("ElectricVehicle")
    ecar = EV.ElectricCar("ABC123", "Tesla", "Model 3", "Blue")
    ebike = EV.ElectricBike("MOTO1", "Zero", "FXE", "Black")
    assert isinstance(ecar, EV.ElectricVehicle)
    assert isinstance(ebike, EV.ElectricVehicle)

@pytest.mark.xfail(reason="Baseline bug: EV finder param mismatch causes NameError", strict=True)
def test_ev_finder_param_mismatch_xfail():
    PM = import_src("ParkingManager")  # safe: UI guarded by main()
    EV = import_src("ElectricVehicle")
    lot = PM.ParkingLot()
    lot.createParkingLot(1, 1, 1)
    lot.evSlots[0] = EV.ElectricCar("R1", "Tesla", "3", "Blue")
    # This uses param name "color" but references undefined 'make' in baseline
    lot.getSlotNumFromMakeEv("Tesla")  # should raise NameError in baseline
