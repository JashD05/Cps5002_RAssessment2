# Techburg/entities.py
class SparePart:
    def __init__(self, size, x, y):
        self.x = x; self.y = y; self.size = size
        self.type = "spare_part"
        
        # --- THIS IS THE FIX ---
        # The enhancement_type is now correctly assigned based on the part's size.
        if self.size == "large":
            self.enhancement_type = "energy_capacity"
            self.color = "orange"
        elif self.size == "medium":
            self.enhancement_type = "vision"
            self.color = "light blue"
        else: # small
            self.enhancement_type = "speed"
            self.color = "light green"

        self.max_corrosion = 1000 # Used for enhancement duration

    def update(self, grid):
        """Entities can have update logic, but parts are static until collected."""
        pass


class RechargeStation:
    def __init__(self, x, y):
        self.x = x; self.y = y
        self.type = "recharge_station"; self.color = "purple"

    def update(self, grid):
        """Stations are static."""
        pass