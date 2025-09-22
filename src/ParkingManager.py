# src/ParkingManager.py
"""
Tkinter UI wired to a pure ParkingService façade.
- No Tk objects created at import time.
- All actions route through ParkingService; UI only renders returned data.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable

from parking_service import ParkingService, VehicleSpec


# ----------------------------- UI Builders --------------------------------- #
def build_lot_section(
    root: tk.Tk,
    num_value: tk.StringVar,
    ev_value: tk.StringVar,
    level_value: tk.StringVar,
    on_create: Callable[[], None],
) -> None:
    tk.Label(root, text="Parking Lot Manager", font="Arial 14 bold").grid(
        row=0, column=0, padx=10, columnspan=4, sticky="w"
    )
    tk.Label(root, text="Lot Creation", font="Arial 12 bold").grid(
        row=1, column=0, padx=10, columnspan=4, sticky="w"
    )

    tk.Label(root, text="Number of Regular Spaces", font="Arial 12").grid(
        row=2, column=0, padx=5, sticky="w"
    )
    tk.Entry(root, textvariable=num_value, width=6, font="Arial 12").grid(
        row=2, column=1, padx=4, pady=2, sticky="w"
    )

    tk.Label(root, text="Number of EV Spaces", font="Arial 12").grid(
        row=2, column=2, padx=5, sticky="w"
    )
    tk.Entry(root, textvariable=ev_value, width=6, font="Arial 12").grid(
        row=2, column=3, padx=4, pady=2, sticky="w"
    )

    tk.Label(root, text="Floor Level", font="Arial 12").grid(
        row=3, column=0, padx=5, sticky="w"
    )
    tk.Entry(root, textvariable=level_value, width=6, font="Arial 12").grid(
        row=3, column=1, padx=4, pady=2, sticky="w"
    )

    tk.Button(
        root,
        command=on_create,
        text="Create Parking Lot",
        font="Arial 12",
        bg="lightblue",
        fg="black",
        activebackground="teal",
        padx=5,
        pady=5,
    ).grid(row=4, column=0, padx=4, pady=4, sticky="w")


def build_car_form(  # noqa: PLR0913
    root: tk.Tk,
    make_value: tk.StringVar,
    model_value: tk.StringVar,
    color_value: tk.StringVar,
    reg_value: tk.StringVar,
    ev_car_value: tk.IntVar,
    ev_motor_value: tk.IntVar,
    on_park: Callable[[], None],
) -> None:
    tk.Label(root, text="Car Management", font="Arial 12 bold").grid(
        row=5, column=0, padx=10, columnspan=4, sticky="w"
    )

    tk.Label(root, text="Make", font="Arial 12").grid(row=6, column=0, padx=5, sticky="w")
    tk.Entry(root, textvariable=make_value, width=12, font="Arial 12").grid(
        row=6, column=1, padx=4, pady=4, sticky="w"
    )

    tk.Label(root, text="Model", font="Arial 12").grid(row=6, column=2, padx=5, sticky="w")
    tk.Entry(root, textvariable=model_value, width=12, font="Arial 12").grid(
        row=6, column=3, padx=4, pady=4, sticky="w"
    )

    tk.Label(root, text="Color", font="Arial 12").grid(row=7, column=0, padx=5, sticky="w")
    tk.Entry(root, textvariable=color_value, width=12, font="Arial 12").grid(
        row=7, column=1, padx=4, pady=4, sticky="w"
    )

    tk.Label(root, text="Registration #", font="Arial 12").grid(
        row=7, column=2, padx=5, sticky="w"
    )
    tk.Entry(root, textvariable=reg_value, width=12, font="Arial 12").grid(
        row=7, column=3, padx=4, pady=4, sticky="w"
    )

    tk.Checkbutton(
        root, text="Electric", variable=ev_car_value, onvalue=1, offvalue=0, font="Arial 12"
    ).grid(column=0, row=8, padx=4, pady=4, sticky="w")
    tk.Checkbutton(
        root, text="Motorcycle", variable=ev_motor_value, onvalue=1, offvalue=0, font="Arial 12"
    ).grid(column=1, row=8, padx=4, pady=4, sticky="w")

    tk.Button(
        root,
        command=on_park,
        text="Park Car",
        font="Arial 11",
        bg="lightblue",
        fg="black",
        activebackground="teal",
        padx=5,
        pady=5,
    ).grid(column=0, row=9, padx=4, pady=4, sticky="w")


def build_remove_section(
    root: tk.Tk,
    slot_value: tk.StringVar,
    ev_car2_value: tk.IntVar,
    on_remove: Callable[[], None],
) -> None:
    tk.Label(root, text="Slot #", font="Arial 12").grid(row=10, column=0, padx=5, sticky="w")
    tk.Entry(root, textvariable=slot_value, width=12, font="Arial 12").grid(
        row=10, column=1, padx=4, pady=4, sticky="w"
    )
    tk.Checkbutton(
        root, text="Remove EV?", variable=ev_car2_value, onvalue=1, offvalue=0, font="Arial 12"
    ).grid(column=2, row=10, padx=4, pady=4, sticky="w")

    tk.Button(
        root,
        command=on_remove,
        text="Remove Car",
        font="Arial 11",
        bg="lightblue",
        fg="black",
        activebackground="teal",
        padx=5,
        pady=5,
    ).grid(column=0, row=11, padx=4, pady=4, sticky="w")


def build_lookup_buttons(
    root: tk.Tk,
    on_slot_by_reg: Callable[[], None],
    on_slot_by_color: Callable[[], None],
    on_reg_by_color: Callable[[], None],
) -> None:
    tk.Label(root, text="", font="Arial 10").grid(row=12, column=0)  # spacer

    tk.Button(
        root,
        command=on_slot_by_reg,
        text="Get Slot ID by Registration #",
        font="Arial 11",
        bg="lightblue",
        fg="black",
        activebackground="teal",
        padx=5,
        pady=5,
    ).grid(column=0, row=13, padx=4, pady=4, sticky="w")

    tk.Button(
        root,
        command=on_slot_by_color,
        text="Get Slot ID by Color",
        font="Arial 11",
        bg="lightblue",
        fg="black",
        activebackground="teal",
        padx=5,
        pady=5,
    ).grid(column=2, row=13, padx=4, pady=4, sticky="w")

    tk.Button(
        root,
        command=on_reg_by_color,
        text="Get Registration # by Color",
        font="Arial 11",
        bg="lightblue",
        fg="black",
        activebackground="teal",
        padx=5,
        pady=5,
    ).grid(column=0, row=14, padx=4, pady=4, sticky="w")


def build_status_section(
    root: tk.Tk,
    tfield: tk.Text,
    on_show_charge: Callable[[], None],
    on_show_status: Callable[[], None],
) -> None:
    tk.Button(
        root,
        command=on_show_charge,
        text="EV Charge Status",
        font="Arial 11",
        bg="lightblue",
        fg="black",
        activebackground="teal",
        padx=5,
        pady=5,
    ).grid(column=2, row=14, padx=4, pady=4, sticky="w")

    tk.Button(
        root,
        command=on_show_status,
        text="Current Lot Status",
        font="Arial 11",
        bg="PaleGreen1",
        fg="black",
        activebackground="PaleGreen3",
        padx=5,
        pady=5,
    ).grid(column=0, row=15, padx=4, pady=4, sticky="w")

    tfield.grid(column=0, row=16, padx=10, pady=10, columnspan=4, sticky="w")


def build_persistence_buttons(
    root: tk.Tk,
    on_save_json: Callable[[], None],
    on_load_json: Callable[[], None],
    on_export_csv: Callable[[], None],
) -> None:
    tk.Label(root, text="", font="Arial 10").grid(row=17, column=0)  # spacer under status area

    tk.Button(
        root,
        command=on_save_json,
        text="Save JSON",
        font="Arial 11",
        bg="LightSteelBlue1",
        fg="black",
        activebackground="LightSteelBlue3",
        padx=5,
        pady=5,
    ).grid(column=0, row=18, padx=4, pady=4, sticky="w")

    tk.Button(
        root,
        command=on_load_json,
        text="Load JSON",
        font="Arial 11",
        bg="LightSteelBlue1",
        fg="black",
        activebackground="LightSteelBlue3",
        padx=5,
        pady=5,
    ).grid(column=1, row=18, padx=4, pady=4, sticky="w")

    tk.Button(
        root,
        command=on_export_csv,
        text="Export CSV",
        font="Arial 11",
        bg="LightSteelBlue1",
        fg="black",
        activebackground="LightSteelBlue3",
        padx=5,
        pady=5,
    ).grid(column=2, row=18, padx=4, pady=4, sticky="w")


# ----------------------------- Application --------------------------------- #
def main() -> None:  # noqa: PLR0915
    # Tk root & state (locals, no globals)
    root = tk.Tk()
    root.geometry("650x900")
    root.resizable(False, False)
    root.title("Parking Lot Manager")

    # state vars
    num_value = tk.StringVar()
    ev_value = tk.StringVar()
    make_value = tk.StringVar()
    model_value = tk.StringVar()
    color_value = tk.StringVar()
    reg_value = tk.StringVar()
    level_value = tk.StringVar(value="1")
    ev_car_value = tk.IntVar(value=0)   # 1 = EV
    ev_car2_value = tk.IntVar(value=0)  # 1 = EV (for remove)
    ev_motor_value = tk.IntVar(value=0)  # 1 = Motorcycle
    slot_value = tk.StringVar()

    tfield = tk.Text(root, width=70, height=18)

    svc: ParkingService | None = None

    # ---------- Callbacks (service-backed) ----------
    def write(msg: str) -> None:
        tfield.insert(tk.INSERT, msg + ("\n" if not msg.endswith("\n") else ""))
        tfield.see(tk.END)

    def makeLot() -> None:
        nonlocal svc
        try:
            cap = int(num_value.get() or "0")
            evc = int(ev_value.get() or "0")
            lvl = int(level_value.get() or "1")
            svc = ParkingService(capacity=cap, ev_capacity=evc, level=lvl)
            write(
                f"Created a parking lot with {cap} regular slots and {evc} EV slots on level {lvl}"
            )
        except ValueError as e:
            write(f"Error: {e}")

    def parkCar() -> None:
        if svc is None:
            write("Please create the parking lot first.")
            return
        spec = VehicleSpec(
            regnum=reg_value.get(),
            make=make_value.get(),
            model=model_value.get(),
            color=color_value.get(),
            fuel="EV" if ev_car_value.get() == 1 else "ICE",
            kind="MOTORCYCLE" if ev_motor_value.get() == 1 else "CAR",
        )
        res = svc.park(spec)
        write(res["message"])

    def removeCar() -> None:
        if svc is None:
            write("Please create the parking lot first.")
            return
        try:
            slot = int(slot_value.get())
        except ValueError:
            write("Slot must be a number")
            return
        res = svc.leave(slot, fuel=("EV" if ev_car2_value.get() == 1 else "ICE"))
        write(res["message"])

    def showStatus() -> None:
        if svc is None:
            write("Please create the parking lot first.")
            return
        write("Vehicles\nSlot\tFloor\tReg No.\t\tColor \t\tMake \t\tModel")
        for r in svc.status_rows():
            write(
                f"{r['slot_ui']}\t{r['level']}\t{r['regnum']}\t\t{r['color']}\t\t{r['make']}\t\t{r['model']}"
            )
        write("\nElectric Vehicles\nSlot\tFloor\tReg No.\t\tColor \t\tMake \t\tModel")
        for r in svc.ev_status_rows():
            write(
                f"{r['slot_ui']}\t{r['level']}\t{r['regnum']}\t\t{r['color']}\t\t{r['make']}\t\t{r['model']}"
            )

    def showChargeStatus() -> None:
        if svc is None:
            write("Please create the parking lot first.")
            return
        write("Electric Vehicle Charge Levels\nSlot\tFloor\tReg No.\t\tCharge %")
        for r in svc.ev_charge_rows():
            write(f"{r['slot_ui']}\t{r['level']}\t{r['regnum']}\t\t{r['charge']}")

    # --------- Step 17: wired lookup handlers ---------
    def lookupSlotByReg() -> None:
        """Find slot(s) for the reg number currently in the Registration field."""
        if svc is None:
            write("Please create the parking lot first.")
            return
        reg = reg_value.get().strip()
        if not reg:
            write("Enter a registration number in the form above, then click the button.")
            return
        slots: list[int] = []
        for row in svc.status_rows():
            if row["regnum"] == reg:
                slots.append(row["slot_ui"])
        for row in svc.ev_status_rows():
            if row["regnum"] == reg:
                slots.append(row["slot_ui"])
        if slots:
            write(f"Registration {reg} found in slot(s): {', '.join(map(str, slots))}")
        else:
            write(f"No slot found for registration {reg}")

    def lookupSlotByColor() -> None:
        if svc is None:
            write("Please create the parking lot first.")
            return
        color = color_value.get().strip()
        if not color:
            write("Enter a color in the form above, then click the button.")
            return
        slots = svc.all_slots_by_color(color)
        if slots:
            write(f"Color {color}: slot(s) {', '.join(map(str, slots))}")
        else:
            write(f"No slots found for color {color}")

    def lookupRegByColor() -> None:
        if svc is None:
            write("Please create the parking lot first.")
            return
        color = color_value.get().strip()
        if not color:
            write("Enter a color in the form above, then click the button.")
            return
        regs = svc.all_regnums_by_color(color)
        if regs:
            write(f"Registration numbers for color {color}: {', '.join(regs)}")
        else:
            write(f"No registrations found for color {color}")

    # --------- Step 19: persistence handlers ---------
    def saveJson() -> None:
        if svc is None:
            messagebox.showinfo("Parking Manager", "Create or load a lot first.")
            return
        path = filedialog.asksaveasfilename(
            title="Save lot as JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            svc.save_json(path)
            write(f"Saved lot to {path}")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Save JSON failed", str(e))

    def loadJson() -> None:
        nonlocal svc
        path = filedialog.askopenfilename(
            title="Load lot JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            svc = ParkingService.load_json(path)
            write(f"Loaded lot from {path}")
            showStatus()
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Load JSON failed", str(e))

    def exportCsv() -> None:
        if svc is None:
            messagebox.showinfo("Parking Manager", "Create or load a lot first.")
            return
        path = filedialog.asksaveasfilename(
            title="Export status CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            svc.save_csv(path, include_ev=True)
            write(f"Exported CSV to {path}")
        except Exception as e:  # noqa: BLE001
            messagebox.showerror("Export CSV failed", str(e))

    # ---------- Build UI ----------
    build_lot_section(root, num_value, ev_value, level_value, makeLot)
    build_car_form(
        root,
        make_value,
        model_value,
        color_value,
        reg_value,
        ev_car_value,
        ev_motor_value,
        parkCar,
    )
    build_remove_section(root, slot_value, ev_car2_value, removeCar)
    build_lookup_buttons(root, lookupSlotByReg, lookupSlotByColor, lookupRegByColor)
    build_status_section(root, tfield, showChargeStatus, showStatus)
    build_persistence_buttons(root, saveJson, loadJson, exportCsv)
    root.geometry("650x980")  # was 650x900

    root.mainloop()


if __name__ == "__main__":
    main()
