from src.parking_service import ParkingService, VehicleSpec

def test_ice_finders_by_make_model_and_color():
    svc = ParkingService(capacity=3, ev_capacity=1, level=1)
    svc.park(VehicleSpec("R1","Honda","Civic","Blue",  "ICE","CAR"))
    svc.park(VehicleSpec("R2","Honda","Accord","Green","ICE","CAR"))
    svc.park(VehicleSpec("R3","Ford","F-150","Blue",   "ICE","TRUCK"))
    assert set(svc.slots_by_make("Honda")) == {1, 2}
    assert svc.slots_by_model("F-150") == [3]
    assert set(svc.all_slots_by_color("Blue")) >= {1, 3}  # may include EVs too if present

def test_cross_cutting_regnums_by_color_includes_ev_and_ice():
    svc = ParkingService(capacity=1, ev_capacity=1, level=1)
    svc.park(VehicleSpec("R1","Honda","Civic","Blue", "ICE","CAR"))
    svc.park(VehicleSpec("E1","Tesla","3","Blue",     "EV","CAR"))
    regs = sorted(svc.all_regnums_by_color("Blue"))
    assert regs == ["E1","R1"]
