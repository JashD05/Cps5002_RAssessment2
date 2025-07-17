# Techburg/entities.py
class SparePart:
    def __init__(self, size, x, y):
        self.x, self.y, self.size = x, y, size
        self.type = "spare_part"
        if self.size == "large": self.color = "orange"
        elif self.size == "medium": self.color = "light blue"
        else: self.color = "light green"
    def update(self, grid): pass

class RechargeStation:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type, self.color = "recharge_station", "purple"
    def update(self, grid): pass    