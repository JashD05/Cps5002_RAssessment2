# Techburg/entities.py
class SparePart:
    def __init__(self, size, x, y):
        self.x, self.y, self.size = x, y, size
        self.type = "spare_part"
        if self.size == "large": self.enhancement_type, self.color = "energy_capacity", "orange"
        elif self.size == "medium": self.enhancement_type, self.color = "vision", "light blue"
        else: self.enhancement_type, self.color = "speed", "light green"
        self.corrosion_level, self.max_corrosion = 0, 1000
    def update(self, grid):
        self.corrosion_level += 1
        if self.corrosion_level >= self.max_corrosion: grid.remove_entity(self)

class RechargeStation:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type, self.color = "recharge_station", "purple"
    def update(self, grid): pass