# agents/survivor_bot.py
import math
from ai.pathfinding import find_path # Kept for potential future use, but not used in move_towards
from entities import SparePart

class SurvivorBot:
    """A bot that collects parts, uses enhancements, and collaborates."""
    def __init__(self, bot_id, x, y, energy=100):
        self.bot_id = bot_id; self.x = x; self.y = y; self.energy = energy
        self.base_max_energy = 100; self.base_speed = 1; self.base_vision = 5
        self.max_energy = self.base_max_energy; self.speed = self.base_speed; self.vision = self.base_vision
        self.energy_depletion_rate = 0.05
        self.carrying_part = None; self.path = []; self.state = "SEARCHING"
        self.type = 'survivor_bot'; self.color = "deep sky blue"
        self.stunned = 0; self.target_entity = None
        self.active_enhancements = {}

    def update(self, grid):
        """Main update logic for the bot."""
        if self.energy <= 0: return
        if self.stunned > 0:
            self.stunned -= 1
            return
        self.energy -= self.energy_depletion_rate
        self.update_enhancements()
        self.execute_state_action(grid)

    def execute_state_action(self, grid):
        """Determines the bot's state and acts accordingly."""
        if self.target_entity and self.target_entity not in grid.entities:
            self.target_entity = None # Clear target if it has been collected/destroyed

        if not self.target_entity:
            if self.energy < 30:
                self.target_entity = self.find_nearest_target(grid, 'recharge_station')
            elif self.carrying_part:
                self.target_entity = self.find_nearest_target(grid, 'recharge_station')
            else:
                self.target_entity = self.find_nearest_target(grid, 'spare_part')

        if self.target_entity:
            if self.x == self.target_entity.x and self.y == self.target_entity.y:
                if self.target_entity.type == 'recharge_station':
                    self.energy = self.max_energy
                    if self.carrying_part:
                        grid.increment_parts_collected()
                        self.carrying_part = None
                elif self.target_entity.type == 'spare_part':
                    self.pickup_part(self.target_entity, grid)
                self.target_entity = None
            else:
                self.move_towards(self.target_entity, grid)

    def move_towards(self, target, grid):
        """Moves one step directly towards the target."""
        dx, dy = 0, 0
        if target.x > self.x: dx = 1
        elif target.x < self.x: dx = -1
        if target.y > self.y: dy = 1
        elif target.y < self.y: dy = -1
        
        new_x, new_y = self.x + dx, self.y + dy
        if grid.is_valid(new_x, new_y):
            grid.move_entity(self, new_x, new_y)

    def find_nearest_target(self, grid, target_type):
        """Finds the nearest target of a given type."""
        targets = [e for e in grid.entities if hasattr(e, 'type') and e.type == target_type]
        if not targets: return None
        return min(targets, key=lambda t: math.hypot(self.x-t.x, self.y-t.y))

    def pickup_part(self, part, grid):
        """Picks up a part."""
        if not self.carrying_part and part in grid.entities:
            self.carrying_part = part
            grid.remove_entity(part)
            self.apply_enhancement(part)

    def apply_enhancement(self, part: SparePart):
        """Applies an enhancement from a part."""
        enhancement_type = part.enhancement_type
        life = part.max_corrosion - part.corrosion_level
        self.active_enhancements[enhancement_type] = life
        self.recalculate_stats()

    def update_enhancements(self):
        """Updates active enhancements."""
        expired = [e for e, life in self.active_enhancements.items() if life <= 0]
        for e in expired: del self.active_enhancements[e]
        if expired: self.recalculate_stats()
        for e in self.active_enhancements: self.active_enhancements[e] -= 1

    def recalculate_stats(self):
        """Recalculates bot stats based on enhancements."""
        self.max_energy = self.base_max_energy + (50 if 'energy_capacity' in self.active_enhancements else 0)
        self.speed = self.base_speed * (1.5 if 'speed' in self.active_enhancements else 1)
        self.vision = self.base_vision + (3 if 'vision' in self.active_enhancements else 0)

# --- Subclasses ---
class GathererBot(SurvivorBot):
    def __init__(self, bot_id, x, y, energy=100):
        super().__init__(bot_id, x, y, energy)
        self.type = 'gatherer_bot'; self.color = "light sea green"

class RepairBot(SurvivorBot):
    def __init__(self, bot_id, x, y, energy=120):
        super().__init__(bot_id, x, y, energy)
        self.type = 'repair_bot'; self.color = "cornflower blue"

class PlayerBot(SurvivorBot):
    def __init__(self, bot_id, x, y, energy=150):
        super().__init__(bot_id, x, y, energy)
        self.type = 'player_bot'; self.color = "orange"; self.energy_depletion_rate = 0.04
        
    def update(self, grid):
        """Player bot's state is mostly controlled manually."""
        if self.energy <= 0: return
        self.energy -= self.energy_depletion_rate; self.update_enhancements()