from src.parking_service import ParkingService, VehicleSpec


def test_lookup_by_registration_across_ev_and_ice():
    svc = ParkingService(capacity=2, ev_capacity=2, level=1)
    svc.park(VehicleSpec("R1","Honda","Civic","Blue","ICE","CAR"))
    svc.park(VehicleSpec("E1","Tesla","3","Blue","EV","CAR"))
    assert svc.first_slot_by_reg("R1") == 1
    assert svc.all_slots_by_reg("E1") == [1]
    assert svc.all_slots_by_reg("NOPE") == []
