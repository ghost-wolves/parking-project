# src/ElectricVehicle.py

class ElectricVehicle:
    def __init__(self, regnum, make, model, color):
        self.regnum = regnum
        self.make = make
        self.model = model
        self.color = color
        self.charge = 0

    def getType(self):
        return "ElectricVehicle"

# ✅ FIXED: now inherit from ElectricVehicle
class ElectricCar(ElectricVehicle):
    def __init__(self, regnum, make, model, color):
        super().__init__(regnum, make, model, color)

    def getType(self):
        return "Car"   # keep baseline behavior for now

class ElectricBike(ElectricVehicle):
    def __init__(self, regnum, make, model, color):
        super().__init__(regnum, make, model, color)

    def getType(self):
        return "Motorcycle"  # baseline behavior
