# src/cli.py
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from parking_service import ParkingService, VehicleSpec


def die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _service_from_args(args: argparse.Namespace) -> ParkingService:
    """
    Helper: either create a fresh lot (if --create* flags are present)
    or load an existing one with --load.
    """
    if getattr(args, "load", None):
        p = Path(args.load)
        if not p.exists():
            die(f"File not found: {p}")
        return ParkingService.load_json(str(p))

    # For commands that need a lot but didn't pass --load, allow on-the-fly create
    cap = getattr(args, "capacity", None)
    evc = getattr(args, "ev_capacity", None)
    lvl = getattr(args, "level", None)
    if cap is not None and evc is not None and lvl is not None:
        return ParkingService(capacity=cap, ev_capacity=evc, level=lvl)

    die("No lot loaded or created. Pass --load FILE or --capacity/--ev-capacity/--level.")


def cmd_create(args: argparse.Namespace) -> None:
    svc = ParkingService(capacity=args.capacity, ev_capacity=args.ev_capacity, level=args.level)
    print(f"Created lot: capacity={svc.capacity} ev_capacity={svc.ev_capacity} level={svc.level}")
    if args.save:
        svc.save_json(args.save)
        print(f"Saved lot to {args.save}")


def cmd_status(args: argparse.Namespace) -> None:
    svc = _service_from_args(args)
    if args.ev:
        print("EV Slots")
        for r in svc.ev_status_rows():
            print(f"{r['slot_ui']}\tL{r['level']}\t{r['regnum']}\t{r['color']}\t{r['make']}\t{r['model']}")
    else:
        print("ICE Slots")
        for r in svc.status_rows():
            print(f"{r['slot_ui']}\tL{r['level']}\t{r['regnum']}\t{r['color']}\t{r['make']}\t{r['model']}")


def cmd_park(args: argparse.Namespace) -> None:
    svc = _service_from_args(args)
    spec = VehicleSpec(
        regnum=args.reg.strip().upper(),
        make=args.make.strip(),
        model=args.model.strip(),
        color=args.color.strip(),
        fuel="EV" if args.ev else "ICE",
        kind=args.kind,
    )
    res = svc.park(spec)
    if args.save:
        svc.save_json(args.save)
    print(json.dumps(res))


def cmd_leave(args: argparse.Namespace) -> None:
    svc = _service_from_args(args)
    out = svc.leave(args.slot_ui, fuel=("EV" if args.ev else "ICE"))
    if args.save:
        svc.save_json(args.save)
    print(json.dumps(out))


def cmd_save(args: argparse.Namespace) -> None:
    svc = _service_from_args(args)
    svc.save_json(args.path)
    print(f"Saved lot to {args.path}")


def cmd_load(args: argparse.Namespace) -> None:
    svc = ParkingService.load_json(args.path)
    print(f"Loaded lot: capacity={svc.capacity} ev_capacity={svc.ev_capacity} level={svc.level}")
    if args.out:
        svc.save_json(args.out)
        print(f"Re-saved lot to {args.out}")


def cmd_export_csv(args: argparse.Namespace) -> None:
    svc = _service_from_args(args)
    svc.save_csv(args.path, include_ev=not args.ice_only)
    print(f"Exported CSV to {args.path}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="parking", description="Parking lot CLI")
    sub = p.add_subparsers(required=True, dest="cmd")

    # create
    sp = sub.add_parser("create", help="Create a new lot (optionally save)")
    sp.add_argument("--capacity", type=int, required=True)
    sp.add_argument("--ev-capacity", type=int, required=True)
    sp.add_argument("--level", type=int, required=True)
    sp.add_argument("--save", type=str, help="Save to JSON after creating")
    sp.set_defaults(func=cmd_create)

    # status (ICE or EV)
    sp = sub.add_parser("status", help="Show status (ICE by default)")
    sp.add_argument("--load", type=str, help="Load lot JSON first")
    sp.add_argument("--capacity", type=int, help="(alt) create capacity if not loading")
    sp.add_argument("--ev-capacity", type=int, help="(alt) create ev capacity if not loading")
    sp.add_argument("--level", type=int, help="(alt) create level if not loading")
    sp.add_argument("--ev", action="store_true", help="Show EV slots instead of ICE")
    sp.set_defaults(func=cmd_status)

    # park
    sp = sub.add_parser("park", help="Park a vehicle")
    sp.add_argument("--load", type=str, help="Load lot JSON first")
    sp.add_argument("--capacity", type=int, help="(alt) create capacity if not loading")
    sp.add_argument("--ev-capacity", type=int, help="(alt) create ev capacity if not loading")
    sp.add_argument("--level", type=int, help="(alt) create level if not loading")
    sp.add_argument("--reg", required=True, type=str)
    sp.add_argument("--make", required=True, type=str)
    sp.add_argument("--model", required=True, type=str)
    sp.add_argument("--color", required=True, type=str)
    sp.add_argument("--ev", action="store_true", help="Fuel is EV (default ICE)")
    sp.add_argument("--kind", choices=["CAR", "MOTORCYCLE", "TRUCK", "BUS"], default="CAR")
    sp.add_argument("--save", type=str, help="Save lot JSON after action")
    sp.set_defaults(func=cmd_park)

    # leave
    sp = sub.add_parser("leave", help="Leave a slot")
    sp.add_argument("--load", type=str, help="Load lot JSON first")
    sp.add_argument("--capacity", type=int, help="(alt) create capacity if not loading")
    sp.add_argument("--ev-capacity", type=int, help="(alt) create ev capacity if not loading")
    sp.add_argument("--level", type=int, help="(alt) create level if not loading")
    sp.add_argument("--slot-ui", dest="slot_ui", type=int, required=True, help="UI slot number (1-based)")
    sp.add_argument("--ev", action="store_true", help="Operate on EV pool")
    sp.add_argument("--save", type=str, help="Save lot JSON after action")
    sp.set_defaults(func=cmd_leave)

    # save
    sp = sub.add_parser("save", help="Save current lot to JSON")
    sp.add_argument("--load", type=str, help="Load lot JSON first")
    sp.add_argument("--capacity", type=int, help="(alt) create capacity if not loading")
    sp.add_argument("--ev-capacity", type=int, help="(alt) create ev capacity if not loading")
    sp.add_argument("--level", type=int, help="(alt) create level if not loading")
    sp.add_argument("path", type=str)
    sp.set_defaults(func=cmd_save)

    # load
    sp = sub.add_parser("load", help="Load lot JSON (and optionally re-save)")
    sp.add_argument("path", type=str)
    sp.add_argument("--out", type=str, help="Write loaded lot to this path")
    sp.set_defaults(func=cmd_load)

    # export-csv
    sp = sub.add_parser("export-csv", help="Export current status to CSV")
    sp.add_argument("--load", type=str, help="Load lot JSON first")
    sp.add_argument("--capacity", type=int, help="(alt) create capacity if not loading")
    sp.add_argument("--ev-capacity", type=int, help="(alt) create ev capacity if not loading")
    sp.add_argument("--level", type=int, help="(alt) create level if not loading")
    sp.add_argument("path", type=str)
    sp.add_argument("--ice-only", action="store_true", help="Export only ICE rows")
    sp.set_defaults(func=cmd_export_csv)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        die(f"Error: {e}")


if __name__ == "__main__":
    raise SystemExit(main())
