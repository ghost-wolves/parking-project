# Parking Lot Manager

A small, testable parking-lot system with:
- Core domain classes (`Vehicle`, `ElectricVehicle`)
- `ParkingService` (pure logic): park/leave, EV vs ICE pools, finders, CSV/JSON
- Tk UI (`ParkingManager.py`) with lookups, persistence buttons, scrollable output
- Optional CLI (`src/cli.py`) for headless usage
- Tests, mypy typings, and ruff lint

## Features
- Separate ICE / EV slot pools with 1-based UI slot numbers
- Vehicle factory for correct subclass creation
- Safe slot state transitions (`Slot`), no sentinel values
- Finders: by make/model/color/registration (UI uses status tables)
- Persistence: JSON save/load; CSV export
- UX: clear output, scrollback, enable/disable controls until lot exists

## Quick Start
```bash
# create venv and install dev tools (optional)
python -m venv .venv && . .venv/Scripts/activate  # Windows (or `source .venv/bin/activate` on mac/linux)
pip install -r requirements-dev.txt

# run UI
python -m src.ParkingManager

# run CLI (examples)
python -m src.cli create --capacity 2 --ev-capacity 2 --level 1 --save lot.json
python -m src.cli park --load lot.json --reg R1 --make Honda --model Civic --color Blue --kind CAR --save lot.json
python -m src.cli status --load lot.json
python -m src.cli export-csv --load lot.json status.csv
