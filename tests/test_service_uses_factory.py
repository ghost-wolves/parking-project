# tests/test_service_uses_factory.py
from src.parking_service import ParkingService, VehicleSpec
import ElectricVehicle as EV
import Vehicle as V

def test_service_parks_ev_bike_via_factory():
    svc = ParkingService(2, 2, 1)
    r = svc.park(VehicleSpec("E1","Zero","FXE","Black", fuel="EV", kind="MOTORCYCLE"))
    assert r["ok"] and r["slot_ui"] == 1
    # Slot now holds the vehicle in .vehicle
    assert isinstance(svc.evSlots[0].vehicle, EV.ElectricBike)

def test_service_parks_truck_via_factory():
    svc = ParkingService(2, 0, 1)
    r = svc.park(VehicleSpec("T1","Ford","F150","Blue", fuel="ICE", kind="TRUCK"))
    assert r["ok"] and r["slot_ui"] == 1
    assert isinstance(svc.slots[0].vehicle, V.Truck)
