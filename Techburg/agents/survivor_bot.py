# File: Techburg/agents/survivor_bot.py
import math
from ai.pathfinding import find_path

class SurvivorBot:
    def __init__(self, bot_id, x, y, energy=100):
        self.bot_id = bot_id
        self.x = x
        self.y = y
        self.energy = energy
        self.energy_depletion_rate = 8
        self.carrying_part = None
        self.path = []
        self.state = "SEARCHING"
        self.type = "survivor_bot"
        self.color = "deep sky blue"

    def update(self, grid):
        if not self.path:
            entity_at_pos = grid.get_entity(self.x, self.y)
            if entity_at_pos:
                if entity_at_pos.type == 'recharge_station' and self.carrying_part:
                    grid.increment_parts_collected()
                    self.carrying_part = None
                    self.state = "SEARCHING"
                    return
                elif entity_at_pos.type == 'spare_part' and not self.carrying_part:
                    self.carrying_part = entity_at_pos
                    grid.remove_entity(entity_at_pos)
                    self.state = "SEARCHING"
                    return

        if self.state == "SEARCHING":
            if self.carrying_part:
                self.state = "MOVING_TO_STATION"
            else:
                target_part = self.find_nearest_target(grid, "spare_part")
                if target_part:
                    path = find_path(grid, (self.x, self.y), (target_part.x, target_part.y))
                    if path: self.path = path
                    self.state = "MOVING_TO_PART"

        elif self.state == "MOVING_TO_PART":
            if not self.path:
                self.state = "SEARCHING"
            else:
                # --- CORRECTED LOGIC ---
                # Pop only ONCE and store the result
                next_pos = self.path.pop(0)
                self.move_to(next_pos[0], next_pos[1], grid)
                # --- END CORRECTION ---

        elif self.state == "MOVING_TO_STATION":
            if not self.path:
                target_station = self.find_nearest_target(grid, "recharge_station")
                if target_station:
                    path = find_path(grid, (self.x, self.y), (target_station.x, target_station.y))
                    if path: self.path = path
                else:
                    self.state = "SEARCHING"
            else:
                # --- CORRECTED LOGIC ---
                # Pop only ONCE and store the result
                next_pos = self.path.pop(0)
                self.move_to(next_pos[0], next_pos[1], grid)
                # --- END CORRECTION ---
                
                if not self.path:
                    self.state = "SEARCHING"

    def find_nearest_target(self, grid, target_type):
        targets = grid.get_all_entities_of_type(target_type)
        if not targets:
            return None
        def toroidal_distance(p1_x, p1_y, p2_x, p2_y):
            dx = abs(p1_x - p2_x)
            dy = abs(p1_y - p2_y)
            shortest_dx = min(dx, grid.width - dx)
            shortest_dy = min(dy, grid.height - dy)
            return math.sqrt(shortest_dx**2 + shortest_dy**2)
        return min(targets, key=lambda t: toroidal_distance(self.x, self.y, t.x, t.y))

    def move_to(self, x, y, grid):
        if self.energy > self.energy_depletion_rate:
            if grid.move_entity(self, x, y):
                self.energy -= self.energy_depletion_rate
        else:
            self.energy = 0

# --- Other Bot Classes (GathererBot, RepairBot, PlayerBot) remain the same ---

class GathererBot(SurvivorBot):
    def __init__(self, bot_id, x, y, energy=100):
        super().__init__(bot_id, x, y, energy)
        self.energy_depletion_rate = 7
        self.type = "gatherer_bot"
        self.color = "light sea green"

class RepairBot(SurvivorBot):
    def __init__(self, bot_id, x, y, energy=100):
        super().__init__(bot_id, x, y, energy)
        self.type = "repair_bot"
        self.color = "cornflower blue"

class PlayerBot(SurvivorBot):
    def __init__(self, bot_id, x, y, energy=100):
        super().__init__(bot_id, x, y, energy)
        self.type = "player_bot"
        self.color = "orange"
        
    def update(self, grid):
        pass