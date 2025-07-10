# agents/survivor_bot.py
import math
from ai.pathfinding import find_path
from entities import SparePart

class SurvivorBot:
    """A bot that collects parts, uses enhancements, and collaborates."""
    def __init__(self, bot_id, x, y, energy=100):
        self.bot_id = bot_id
        self.x = x
        self.y = y
        self.energy = energy
        
        # Base stats
        self.base_max_energy = 100
        self.base_speed = 1
        self.base_vision = 5
        
        # Current stats
        self.max_energy = self.base_max_energy
        self.speed = self.base_speed
        self.vision = self.base_vision

        self.energy_depletion_rate = 0.05
        self.carrying_part = None
        self.path = []
        self.state = "SEARCHING"
        self.type = 'survivor_bot'
        self.color = "deep sky blue"
        self.stunned = 0
        self.target_entity = None
        
        self.active_enhancements = {}

    def update(self, grid):
        """Main update logic for the bot."""
        if self.energy <= 0:
            return # Bot is out of energy, do nothing
            
        if self.stunned > 0:
            self.stunned -= 1
            return
            
        self.energy -= self.energy_depletion_rate
        self.update_enhancements(grid)
        
        self.execute_state_action(grid)

    def execute_state_action(self, grid):
        """Determines the bot's state and acts accordingly."""
        # 1. Decide what the goal is
        if self.energy < 30:
            self.state = "FLEEING_TO_STATION"
            self.target_entity = self.find_nearest_target(grid, 'recharge_station')
        elif self.carrying_part:
            self.state = "MOVING_TO_STATION"
            self.target_entity = self.find_nearest_target(grid, 'recharge_station')
        else:
            self.state = "SEARCHING"
            self.target_entity = self.find_nearest_target(grid, 'spare_part')

        # 2. Act on the goal
        if self.target_entity:
            # Check if we have arrived at the target
            if self.x == self.target_entity.x and self.y == self.target_entity.y:
                if self.target_entity.type == 'recharge_station':
                    self.energy = self.max_energy
                    if self.carrying_part:
                        grid.increment_parts_collected()
                        self.carrying_part = None
                elif self.target_entity.type == 'spare_part':
                    self.pickup_part(self.target_entity, grid)
                
                self.target_entity = None # Clear target to find a new one next turn
            else:
                # If not at the target, move towards it
                self.move_towards(self.target_entity, grid)

    def move_towards(self, target, grid):
        """Finds a path and moves one step."""
        path = find_path(grid, (self.x, self.y), (target.x, target.y))
        if path:
            next_pos = path[0]
            grid.move_entity(self, next_pos[0], next_pos[1])

    def find_nearest_target(self, grid, target_type):
        """Finds the nearest visible target of a given type."""
        targets = [e for e in grid.entities if e.type == target_type]
        if not targets:
            return None
            
        visible_targets = [t for t in targets if math.hypot(self.x-t.x, self.y-t.y) <= self.vision]
        if not visible_targets:
            return None
        return min(visible_targets, key=lambda t: math.hypot(self.x-t.x, self.y-t.y))

    def pickup_part(self, part, grid):
        """Picks up a part and applies its enhancement."""
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

    def update_enhancements(self, grid):
        """Corrodes enhancements and removes them when they expire."""
        expired = []
        for enhancement, life in self.active_enhancements.items():
            self.active_enhancements[enhancement] -= 1
            if self.active_enhancements[enhancement] <= 0:
                expired.append(enhancement)
        
        if expired:
            for enhancement in expired:
                del self.active_enhancements[enhancement]
            self.recalculate_stats()

    def recalculate_stats(self):
        """Recalculates bot stats based on active enhancements."""
        self.max_energy = self.base_max_energy
        self.speed = self.base_speed
        self.vision = self.base_vision
        if 'energy_capacity' in self.active_enhancements:
            self.max_energy += 50
        if 'speed' in self.active_enhancements:
            self.speed = self.base_speed * 1.5
        if 'vision' in self.active_enhancements:
            self.vision = self.base_vision + 3

# --- Subclasses ---
class GathererBot(SurvivorBot):
    def __init__(self, bot_id, x, y, energy=100):
        super().__init__(bot_id, x, y, energy)
        self.type = 'gatherer_bot'
        self.color = "light sea green"

class RepairBot(SurvivorBot):
    def __init__(self, bot_id, x, y, energy=120):
        super().__init__(bot_id, x, y, energy)
        self.type = 'repair_bot'
        self.color = "cornflower blue"

class PlayerBot(SurvivorBot):
    def __init__(self, bot_id, x, y, energy=150):
        super().__init__(bot_id, x, y, energy)
        self.type = 'player_bot'
        self.color = "orange"
        self.energy_depletion_rate = 0.04
        
    def update(self, grid):
        """Player bot's state is mostly controlled manually."""
        if self.energy <= 0:
            return
        self.energy -= self.energy_depletion_rate
        self.update_enhancements(grid)