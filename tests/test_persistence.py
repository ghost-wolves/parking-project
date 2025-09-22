import json
import os
import tempfile

from src.parking_service import ParkingService, VehicleSpec

def test_to_from_dict_roundtrip():
    svc = ParkingService(2, 2, 1)
    svc.park(VehicleSpec("R1","Honda","Civic","Blue","ICE","CAR"))
    svc.park(VehicleSpec("E1","Tesla","3","Red","EV","CAR"))
    d = svc.to_dict()
    clone = ParkingService.from_dict(d)

    # Same sizes and level
    assert clone.capacity == 2 and clone.ev_capacity == 2 and clone.level == 1
    # Same visible rows
    assert clone.status_rows() == svc.status_rows()
    assert clone.ev_status_rows() == svc.ev_status_rows()

def test_json_save_load(tmp_path):
    svc = ParkingService(1, 1, 2)
    svc.park(VehicleSpec("TRK1","Ford","F-150","Black","ICE","TRUCK"))
    svc.park(VehicleSpec("EV1","Nissan","Leaf","Green","EV","CAR"))
    p = tmp_path / "lot.json"
    svc.save_json(str(p))
    assert p.exists()

    loaded = ParkingService.load_json(str(p))
    assert loaded.level == 2
    assert loaded.status_rows() == svc.status_rows()
    assert loaded.ev_status_rows() == svc.ev_status_rows()

def test_csv_export(tmp_path):
    svc = ParkingService(2, 1, 1)
    svc.park(VehicleSpec("R1","Honda","Accord","Blue","ICE","CAR"))
    svc.park(VehicleSpec("E1","Zero","FXE","Black","EV","MOTORCYCLE"))

    p = tmp_path / "status.csv"
    svc.save_csv(str(p))
    assert p.exists()
    content = p.read_text(encoding="utf-8").strip().splitlines()
    assert content[0].startswith("slot_ui,level,regnum,color,make,model,fuel")
    assert any(",EV" in line for line in content[1:])
