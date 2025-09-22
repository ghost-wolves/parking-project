
---

# `docs/USER_GUIDE.md`

```markdown
# User Guide (Tk UI)

1. **Create Parking Lot**
   - Enter *Regular Spaces*, *EV Spaces*, and *Floor Level*.
   - Click **Create Parking Lot**.
   - Lookup and persistence buttons enable after a lot exists.

2. **Park a Vehicle**
   - Enter **Make/Model/Color/Registration**.
   - Check **Electric** if EV; **Motorcycle** for two-wheelers.
   - Click **Park Car**. Message appears in the output panel.

3. **Remove a Vehicle**
   - Enter **Slot #** (1-based UI slot number).
   - Check **Remove EV?** if removing from EV pool.
   - Click **Remove Car**.

4. **Lookups**
   - **Get Slot ID by Registration #** uses the reg field.
   - **Get Slot ID by Color** uses the color field.
   - **Get Registration # by Color** lists regs for that color.

5. **Status / EV Charge**
   - **Current Lot Status** prints ICE status then EV status.
   - **EV Charge Status** shows EV charge percent placeholders.

6. **Persistence**
   - **Save JSON** / **Load JSON** / **Export CSV**.
   - After loading, status is shown and buttons stay enabled.

7. **Output Panel**
   - Scroll with the scrollbar; **Clear Output** empties the pane.
