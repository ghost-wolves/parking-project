# tests/test_parking_service_roundtrip.py
from src.parking_service import ParkingService, VehicleSpec


def test_roundtrip_park_leave_ice():
    svc = ParkingService(2, 1, 1)
    r = svc.park(VehicleSpec("R1", "Honda", "Civic", "Blue", fuel="ICE", kind="CAR"))
    assert r["ok"] and r["slot_ui"] == 1
    r2 = svc.leave(r["slot_ui"], fuel="ICE")
    assert r2["ok"]

def test_roundtrip_park_leave_ev():
    svc = ParkingService(2, 1, 1)
    r = svc.park(VehicleSpec("E1", "Tesla", "3", "White", fuel="EV", kind="CAR"))
    assert r["ok"] and r["slot_ui"] == 1
    r2 = svc.leave(r["slot_ui"], fuel="EV")
    assert r2["ok"]
