# File: Techburg/entities.py

class SparePart:
    def __init__(self, size, x, y):
        self.size = size
        self.x = x
        self.y = y
        self.type = "spare_part"
        
        # Set color based on size
        color_map = {"small": "cyan", "medium": "magenta", "large": "yellow"}
        self.color = color_map.get(size, "white")

    def update(self, grid):
        pass # Parts don't do anything on their own

class RechargeStation:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "recharge_station"
        self.color = "purple"

    def update(self, grid):
        pass # Stations don't do anything