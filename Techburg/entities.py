# Techburg/entities.py
import random
# The problematic import has been removed.

class SparePart:
    def __init__(self, size, x, y):
        self.x, self.y, self.size = x, y, size; self.type = "spare_part"
        self.enhancement_value = 100.0
        if self.size == "large": self.enhancement_type, self.color = "energy_capacity", "orange"
        elif self.size == "medium": self.enhancement_type, self.color = "vision", "light blue"
        else: self.enhancement_type, self.color = "speed", "light green"

    def update(self, grid):
        """Corrodes the part over time, devaluing it."""
        self.enhancement_value *= 0.999
        if self.enhancement_value < 10:
            grid.log(f"[EVENT] A {self.size} part corroded away.")
            grid.increment_parts_corroded()
            grid.remove_entity(self)

class RechargeStation:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type, self.color = "recharge_station", "purple"
        self.max_capacity = 5
        self.creation_chance = 0.005

    def update(self, grid):
        """Check for bot creation when a gatherer and repair bot are present."""
        bots_here = grid.get_bots_at_location(self.x, self.y)
        has_gatherer = any(b.type == 'gatherer_bot' for b in bots_here)
        has_repair = any(b.type == 'repair_bot' for b in bots_here)

        if has_gatherer and has_repair and len(bots_here) < self.max_capacity:
            if random.random() < self.creation_chance:
                # Find an empty adjacent spot for the new bot
                for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                    new_x, new_y = self.x + dx, self.y + dy
                    if grid.is_valid(new_x, new_y) and not grid.get_entity(new_x, new_y):
                        from agents.survivor_bot import GathererBot, RepairBot # Local import to prevent circular dependency
                        new_bot_type = random.choice([GathererBot, RepairBot])
                        new_bot = new_bot_type(f"new_bot_{random.randint(100,999)}", new_x, new_y)
                        grid.add_entity(new_bot)
                        grid.log(f"[SUCCESS] Bots collaborated to create a new {new_bot.type}!")
                        break