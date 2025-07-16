# Techburg/agents/survivor_bot.py
import math
from entities import SparePart

class SurvivorBot:
    def __init__(self, bot_id, x, y, energy):
        self.bot_id = bot_id; self.x = x; self.y = y; self.energy = energy
        self.base_max_energy = 200; self.base_speed = 1; self.base_vision = 5
        self.max_energy, self.speed, self.vision = self.base_max_energy, self.base_speed, self.base_vision
        self.energy_depletion_rate = 0.1
        self.carrying_part, self.target_entity = None, None
        self.type = 'survivor_bot'; self.color = "deep sky blue"
        self.stunned, self.active_enhancements = 0, {}

    def update(self, grid):
        if self.energy <= 0: return
        if self.stunned > 0: self.stunned -= 1; grid.log(f"[STATUS] {self.bot_id} is stunned."); return
        self.energy -= self.energy_depletion_rate
        self.update_enhancements()
        self.execute_state_action(grid)

    def execute_state_action(self, grid):
        if not self.target_entity or self.target_entity not in grid.entities:
            self.get_new_goal(grid)
        
        if self.target_entity:
            if self.x == self.target_entity.x and self.y == self.target_entity.y:
                self.handle_arrival(self.target_entity, grid)
            else:
                self.move_towards(self.target_entity, grid)

    def get_new_goal(self, grid):
        target = None
        if self.energy < self.max_energy * 0.4:
            target = self.find_nearest_target(grid, 'recharge_station')
            if target: grid.log(f"[AI] {self.bot_id} seeking energy at ({target.x},{target.y}).")
        elif self.carrying_part:
            target = self.find_nearest_target(grid, 'recharge_station')
            if target: grid.log(f"[AI] {self.bot_id} delivering part.")
        else:
            target = self.find_nearest_target(grid, 'spare_part')
            if target: grid.log(f"[AI] {self.bot_id} targeting part at ({target.x},{target.y}).")
        self.target_entity = target
    
    def move_towards(self, target, grid):
        dx, dy = 0, 0
        if target.x > self.x: dx = 1
        elif target.x < self.x: dx = -1
        if target.y > self.y: dy = 1
        elif target.y < self.y: dy = -1
        new_x, new_y = self.x + dx, self.y + dy
        grid.move_entity(self, new_x, new_y)

    def handle_arrival(self, entity, grid):
        if entity.type == 'recharge_station':
            grid.log(f"[EVENT] {self.bot_id} recharged to {int(self.max_energy)} energy.")
            self.energy = self.max_energy
            if self.carrying_part: 
                grid.increment_parts_collected()
                grid.log(f"[SUCCESS] {self.bot_id} delivered a {self.carrying_part.size} part! Total: {grid.parts_collected}")
                self.carrying_part = None
        elif entity.type == 'spare_part':
            self.pickup_part(entity, grid)
        self.target_entity = None

    def find_nearest_target(self, grid, target_type):
        targets = [e for e in grid.entities if e.type == target_type]
        return min(targets, key=lambda t:math.hypot(self.x-t.x, self.y-t.y)) if targets else None

    def pickup_part(self, part, grid):
        if not self.carrying_part and part in grid.entities:
            grid.log(f"[EVENT] {self.bot_id} picked up a {part.size} part.")
            self.carrying_part = part
            grid.remove_entity(part); self.apply_enhancement(part)
            
    def apply_enhancement(self, part):
        self.active_enhancements[part.enhancement_type] = getattr(part, 'max_corrosion', 1000)
        self.recalculate_stats()

    def update_enhancements(self):
        expired = [e for e, life in self.active_enhancements.items() if life <= 0]
        for e in expired: del self.active_enhancements[e]
        if expired: self.recalculate_stats()
        for e in self.active_enhancements: self.active_enhancements[e] -= 1

    def recalculate_stats(self):
        self.max_energy = self.base_max_energy + (100 if 'energy_capacity' in self.active_enhancements else 0)
        self.speed = self.base_speed * (1.5 if 'speed' in self.active_enhancements else 1)
        self.vision = self.base_vision + (3 if 'vision' in self.active_enhancements else 0)

class GathererBot(SurvivorBot):
    def __init__(self, bot_id, x, y): super().__init__(bot_id, x, y, energy=200); self.type = 'gatherer_bot'; self.color = "light sea green"
class RepairBot(SurvivorBot):
    def __init__(self, bot_id, x, y): super().__init__(bot_id, x, y, energy=250); self.type = 'repair_bot'; self.color = "cornflower blue"
class PlayerBot(SurvivorBot):
    def __init__(self, bot_id, x, y):
        super().__init__(bot_id, x, y, energy=300)
        self.type = 'player_bot'; self.color = "orange"
        self.energy_depletion_rate = 0.08
    def update(self, grid):
        if self.energy <= 0: return
        if self.stunned > 0: self.stunned -= 1; grid.log(f"[STATUS] {self.bot_id} is stunned."); return
        self.energy -= self.energy_depletion_rate
        self.update_enhancements()
        self.execute_state_action(grid)