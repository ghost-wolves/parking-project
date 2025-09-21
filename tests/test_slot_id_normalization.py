from src.parking_service import ParkingService, VehicleSpec


def test_ui_slot_is_array_index_plus_one_for_ice():
    svc = ParkingService(2, 0, 1)
    r = svc.park(VehicleSpec("R1", "Honda", "Civic", "Blue", "ICE", "CAR"))
    assert r["ok"] and r["slot_ui"] == 1
    # Next park should allocate the next index (1 -> UI 2)
    r2 = svc.park(VehicleSpec("R2", "Toyota", "Corolla", "Red", "ICE", "CAR"))
    assert r2["ok"] and r2["slot_ui"] == 2 # noqa: PLR2004

def test_ui_slot_is_array_index_plus_one_for_ev():
    svc = ParkingService(0, 2, 1)
    r = svc.park(VehicleSpec("E1", "Tesla", "3", "White", "EV", "CAR"))
    assert r["ok"] and r["slot_ui"] == 1
    r2 = svc.park(VehicleSpec("E2", "Nissan", "Leaf", "Green", "EV", "CAR"))
    assert r2["ok"] and r2["slot_ui"] == 2 # noqa: PLR2004

def test_leave_uses_ui_slot_number_safely():
    svc = ParkingService(2, 1, 1)
    r = svc.park(VehicleSpec("R1", "Honda", "Civic", "Blue", "ICE", "CAR"))
    assert r["ok"] and r["slot_ui"] == 1 # noqa: PLR2004
    out = svc.leave(1, fuel="ICE")
    assert out["ok"]
    # leaving same slot again should be invalid
    out2 = svc.leave(1, fuel="ICE")
    assert out2["ok"] is False and "invalid" in out2["message"].lower()
