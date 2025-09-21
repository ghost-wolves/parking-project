import pytest

from src.parking_service import ParkingService, VehicleSpec


def test_cannot_construct_with_zero_capacities():
    with pytest.raises(ValueError):
        ParkingService(0, 0, 1)

def test_park_requires_nonblank_registration():
    svc = ParkingService(1, 0, 1)
    res = svc.park(VehicleSpec("   ", "Make", "Model", "Blue", "ICE", "CAR"))
    assert res["ok"] is False and "registration" in res["message"].lower()

def test_parking_lot_full_messages_are_specific():
    svc = ParkingService(1, 0, 1)
    ok = svc.park(VehicleSpec("R1", "M", "X", "Blue", "ICE", "CAR"))
    assert ok["ok"]
    full = svc.park(VehicleSpec("R2", "M", "X", "Red", "ICE", "CAR"))
    assert full["ok"] is False and "full" in full["message"].lower()

def test_leave_out_of_range_and_empty_slot():
    svc = ParkingService(1, 0, 1)
    # slot numbering is 1-based externally; 2 is out-of-range here
    bad = svc.leave(2, fuel="ICE")
    assert bad["ok"] is False and "invalid" in bad["message"].lower()

    # leave empty slot 1
    empty = svc.leave(1, fuel="ICE")
    assert empty["ok"] is False and "invalid" in empty["message"].lower()

def test_finders_ignore_blank_queries():
    svc = ParkingService(2, 2, 1)
    assert svc.slots_by_make("") == []
    assert svc.slots_by_model("  ") == []
    assert svc.ev_slots_by_make("") == []
    assert svc.ev_slots_by_model("  ") == []
    assert svc.all_slots_by_color(" \t ") == []
    assert svc.all_regnums_by_color("") == []

def test_whitespace_is_trimmed_on_park():
    svc = ParkingService(1, 0, 1)
    r = svc.park(VehicleSpec(" R1 ", " Honda ", " Civic ", " Blue ", "ICE", "CAR"))
    assert r["ok"]
    row = svc.status_rows()[0]
    # We trimmed in park(); stored values are trimmed
    assert row["regnum"] == "R1" and row["make"] == "Honda" and row["model"] == "Civic" and row["color"] == "Blue"
