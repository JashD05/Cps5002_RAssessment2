# Techburg/entities.py
import random

class SparePart:
    def __init__(self, size, x, y):
        self.x, self.y, self.size = x, y, size; self.type = "spare_part"
        self.enhancement_value = 100.0
        if self.size == "large": self.enhancement_type, self.color = "energy_capacity", "orange"
        elif self.size == "medium": self.enhancement_type, self.color = "vision", "light blue"
        else: self.enhancement_type, self.color = "speed", "light green"

    def update(self, grid):
        """Corrodes the part over time, devaluing it."""
        self.enhancement_value *= 0.999 # Lose 0.1% of value each step
        if self.enhancement_value < 10:
            grid.log(f"[EVENT] A {self.size} part corroded away at ({self.x},{self.y}).")
            grid.increment_parts_corroded()
            grid.remove_entity(self)

class RechargeStation:
    def __init__(self, x, y):
        self.x, self.y = x, y; self.type = "recharge_station"; self.color = "purple"
        self.max_capacity = 5; self.gatherer_creation_chance = 0.002; self.repairer_creation_chance = 0.001

    def update(self, grid):
        """Handle information sharing and bot creation."""
        bots_here = grid.get_bots_at_location(self.x, self.y)
        if len(bots_here) > 1:
            all_known_parts = set()
            all_known_threats = set()
            for bot in bots_here:
                if hasattr(bot, 'known_parts'): all_known_parts.update(bot.known_parts)
                if hasattr(bot, 'known_threats'): all_known_threats.update(bot.known_threats)
            
            grid.shared_knowledge['parts'].update(all_known_parts)
            grid.shared_knowledge['threats'].update(all_known_threats)

        has_gatherer = any(b.type == 'gatherer_bot' for b in bots_here)
        has_repair = any(b.type == 'repair_bot' for b in bots_here)

        if has_gatherer and has_repair and len(bots_here) < self.max_capacity:
            if random.random() < self.gatherer_creation_chance:
                self.create_new_bot(grid, 'gatherer_bot')
            if random.random() < self.repairer_creation_chance:
                self.create_new_bot(grid, 'repairer_bot')

    def create_new_bot(self, grid, bot_type_str):
        from agents.survivor_bot import GathererBot, RepairBot # Local import
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            new_x, new_y = self.x+dx, self.y+dy
            if grid.is_valid(new_x, new_y) and not grid.get_entity(new_x, new_y):
                bot_class = GathererBot if bot_type_str == 'gatherer_bot' else RepairBot
                new_bot = bot_class(f"new_{bot_type_str[:4]}_{random.randint(100,999)}", new_x, new_y)
                grid.add_entity(new_bot)
                grid.log(f"[SUCCESS] Bots collaborated to create a new {new_bot.type}!")
                break