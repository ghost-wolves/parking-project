from src.parking_service import ParkingService, VehicleSpec

def test_service_constructs_and_validates_sizes():
    svc = ParkingService(capacity=5, ev_capacity=2, level=1)
    assert svc.capacity == 5 and svc.ev_capacity == 2 and svc.level == 1

def test_service_rejects_bad_sizes():
    for args in [
        dict(capacity=-1, ev_capacity=0, level=1),
        dict(capacity=0, ev_capacity=0, level=1),
        dict(capacity=1, ev_capacity=1, level=0),
    ]:
        try:
            ParkingService(**args)  # type: ignore[arg-type]
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")

def test_park_validates_registration_required():
    svc = ParkingService(5, 2, 1)
    spec = VehicleSpec(regnum="  ", make="Tesla", model="3", color="Blue", fuel="EV", kind="CAR")
    res = svc.park(spec)
    assert res["ok"] is False
    assert "registration" in res["message"].lower()

def test_leave_validates_slot_number():
    svc = ParkingService(5, 2, 1)
    res = svc.leave(0)
    assert res["ok"] is False
    assert "slot" in res["message"].lower()
