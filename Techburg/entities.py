# Techburg/entities.py
import random

class SparePart:
    """A spare part that can be picked up by bots and provides enhancements."""
    def __init__(self, size, x, y):
        self.size = size
        self.x = x
        self.y = y
        self.type = "spare_part"
        
        # Determine enhancement and color based on size
        if self.size == "large":
            self.enhancement_type = "energy_capacity"
            self.color = "orange"
        elif self.size == "medium":
            self.enhancement_type = "vision"
            self.color = "light blue"
        else: # small
            self.enhancement_type = "speed"
            self.color = "light green"
        
        self.corrosion_level = 0
        self.max_corrosion = 1000 # Steps until part is fully corroded and disappears

    def update(self, grid):
        """Corrodes the part over time and eventually removes it."""
        self.corrosion_level += 1
        
        # Change color to indicate corrosion
        if self.corrosion_level > self.max_corrosion * 0.75:
            self.color = "dark gray"
        
        if self.corrosion_level >= self.max_corrosion:
            grid.remove_entity(self)
            print(f"A part at ({self.x}, {self.y}) corroded away.")


class RechargeStation:
    """A station for bots to recharge."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "recharge_station"
        self.color = "purple"

    def update(self, grid):
        """Stations are static and don't need updates."""
        pass