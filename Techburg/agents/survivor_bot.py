# Techburg/agents/survivor_bot.py
import math
from entities import SparePart

class SurvivorBot:
    def __init__(self, bot_id, x, y, energy):
        self.bot_id = bot_id; self.x = x; self.y = y; self.energy = energy
        self.max_energy, self.energy_depletion_rate = 200, 0.1
        self.carrying_part, self.target_entity = None, None
        self.type = 'survivor_bot'; self.color = "deep sky blue"

    def update(self, grid):
        self.energy -= self.energy_depletion_rate
        if not self.target_entity or self.target_entity not in grid.entities:
            self.get_new_goal(grid)
        if self.target_entity:
            if self.x == self.target_entity.x and self.y == self.target_entity.y: self.handle_arrival(grid)
            else: self.move_towards(self.target_entity, grid)

    def get_new_goal(self, grid):
        if self.energy < self.max_energy * 0.4: self.target_entity = self.find_nearest(grid, 'recharge_station')
        elif self.carrying_part: self.target_entity = self.find_nearest(grid, 'recharge_station')
        else: self.target_entity = self.find_nearest(grid, 'spare_part')
    
    def move_towards(self, target, grid):
        dx = 1 if target.x > self.x else -1 if target.x < self.x else 0
        dy = 1 if target.y > self.y else -1 if target.y < self.y else 0
        grid.move_entity(self, self.x + dx, self.y + dy)

    def handle_arrival(self, grid):
        if self.target_entity.type == 'recharge_station':
            self.energy = self.max_energy
            grid.log(f"[{self.bot_id}] Recharged to full energy.")
            if self.carrying_part:
                grid.increment_parts_collected()
                grid.log(f"[{self.bot_id}] Delivered a part! Total: {grid.parts_collected}")
                self.carrying_part = None
        elif self.target_entity.type == 'spare_part':
            self.carrying_part = self.target_entity
            grid.remove_entity(self.target_entity)
            grid.log(f"[{self.bot_id}] Picked up a {self.carrying_part.size} part.")
        self.target_entity = None

    def find_nearest(self, grid, target_type):
        targets = [e for e in grid.entities if e.type == target_type]
        return min(targets, key=lambda t:math.hypot(self.x-t.x, self.y-t.y)) if targets else None

class GathererBot(SurvivorBot):
    def __init__(self, bot_id, x, y): super().__init__(bot_id, x, y, 200); self.type = 'gatherer_bot'; self.color = "light sea green"
class RepairBot(SurvivorBot):
    def __init__(self, bot_id, x, y): super().__init__(bot_id, x, y, 250); self.type = 'repair_bot'; self.color = "cornflower blue"
class PlayerBot(SurvivorBot):
    def __init__(self, bot_id, x, y): super().__init__(bot_id, x, y, 300); self.type = 'player_bot'; self.color = "orange"