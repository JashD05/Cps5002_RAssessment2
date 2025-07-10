# agents/survivor_bot.py
import math
from ai.pathfinding import find_path 
from entities import SparePart

class SurvivorBot:
    """A bot that collects parts, uses enhancements, and collaborates."""
    def __init__(self, bot_id, x, y, energy):
        self.bot_id = bot_id; self.x = x; self.y = y
        
        self.base_max_energy = 200
        self.energy = energy 
        
        self.base_speed = 1; self.base_vision = 5
        self.max_energy = self.base_max_energy; self.speed = self.base_speed; self.vision = self.base_vision
        
        self.energy_depletion_rate = 0.08
        
        self.carrying_part = None; self.path = []; self.state = "SEARCHING"
        self.type = 'survivor_bot'; self.color = "deep sky blue"
        self.stunned = 0; self.target_entity = None; self.assisting_bot = None
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
        # --- High-level decision making ---
        # 1. Check for nearby allies in critical need of help.
        bot_to_help = self.find_ally_in_need(grid)
        if bot_to_help:
            self.state = "ASSISTING"
            self.assisting_bot = bot_to_help
            if self.carrying_part: # Drop parts to save a teammate
                self.drop_part(grid)
            self.target_entity = self.find_nearest_target(grid, 'recharge_station')
        
        # 2. If not assisting, determine personal goal.
        else:
            self.state = "IDLE" # Reset state
            self.assisting_bot = None
            if self.energy < self.max_energy * 0.4:
                self.state = "FLEEING_TO_STATION"
                self.target_entity = self.find_nearest_target(grid, 'recharge_station')
            elif self.carrying_part:
                self.state = "MOVING_TO_STATION"
                self.target_entity = self.find_nearest_target(grid, 'recharge_station')
            else:
                self.state = "SEARCHING"
                self.target_entity = self.find_nearest_target(grid, 'spare_part')
        
        # --- Act on the decided goal ---
        if self.target_entity:
            if self.x == self.target_entity.x and self.y == self.target_entity.y:
                self.handle_arrival(grid)
            else:
                self.move_towards(self.target_entity, grid)
    
    def handle_arrival(self, grid):
        """Handles the logic when a bot arrives at its target."""
        if self.target_entity.type == 'recharge_station':
            self.energy = self.max_energy
            if self.carrying_part:
                grid.increment_parts_collected()
                self.carrying_part = None
        elif self.target_entity.type == 'spare_part':
            self.pickup_part(self.target_entity, grid)
        self.target_entity = None


    def find_ally_in_need(self, grid):
        """Finds a nearby allied bot with critical energy."""
        for bot in grid.get_all_bots():
            # Don't try to help the player or itself
            if bot is self or bot.type == 'player_bot':
                continue
            
            # Check for low energy within vision range
            if bot.energy < bot.max_energy * 0.2:
                if math.hypot(self.x - bot.x, self.y - bot.y) <= self.vision:
                    return bot
        return None

    def move_towards(self, target, grid):
        """Moves one step directly towards the target."""
        dx, dy = 0, 0
        if target.x > self.x: dx = 1
        elif target.x < self.x: dx = -1
        if target.y > self.y: dy = 1
        elif target.y < self.y: dy = -1
        
        new_x, new_y = self.x + dx, self.y + dy
        entity_at_new_pos = grid.get_entity(new_x, new_y)
        if grid.is_valid(new_x, new_y) and not (entity_at_new_pos and isinstance(entity_at_new_pos, SurvivorBot)):
            grid.move_entity(self, new_x, new_y)

    def find_nearest_target(self, grid, target_type):
        """Finds the nearest target of a given type."""
        targets = [e for e in grid.entities if hasattr(e, 'type') and e.type == target_type]
        if not targets: return None
        return min(targets, key=lambda t: math.hypot(self.x - t.x, self.y - t.y))

    def pickup_part(self, part, grid):
        """Picks up a part."""
        if not self.carrying_part and part in grid.entities:
            self.carrying_part = part
            grid.remove_entity(part)
            self.apply_enhancement(part)
            
    def drop_part(self, grid):
        """Drops the currently held part to assist another bot."""
        if self.carrying_part:
            part = self.carrying_part
            part.x, part.y = self.x, self.y
            grid.add_entity(part)
            self.carrying_part = None

    def apply_enhancement(self, part: SparePart):
        """Applies an enhancement from a part."""
        self.active_enhancements[part.enhancement_type] = part.max_corrosion - part.corrosion_level
        self.recalculate_stats()

    def update_enhancements(self):
        """Updates active enhancements."""
        expired = [e for e, life in self.active_enhancements.items() if life <= 0]
        for e in expired: del self.active_enhancements[e]
        if expired: self.recalculate_stats()
        for e in self.active_enhancements: self.active_enhancements[e] -= 1

    def recalculate_stats(self):
        """Recalculates bot stats based on enhancements."""
        self.max_energy = self.base_max_energy + (100 if 'energy_capacity' in self.active_enhancements else 0)
        self.speed = self.base_speed * (1.5 if 'speed' in self.active_enhancements else 1)
        self.vision = self.base_vision + (3 if 'vision' in self.active_enhancements else 0)

# --- Subclasses with specialized roles ---
class GathererBot(SurvivorBot):
    """More focused on collecting parts."""
    def __init__(self, bot_id, x, y):
        super().__init__(bot_id, x, y, energy=200)
        self.type = 'gatherer_bot'; self.color = "light sea green"

class RepairBot(SurvivorBot):
    """A support bot, more likely to help others."""
    def __init__(self, bot_id, x, y):
        super().__init__(bot_id, x, y, energy=250)
        self.type = 'repair_bot'; self.color = "cornflower blue"
        # Has better vision to spot allies in need
        self.base_vision = 7
        self.vision = self.base_vision

class PlayerBot(SurvivorBot):
    def __init__(self, bot_id, x, y):
        super().__init__(bot_id, x, y, energy=300)
        self.type = 'player_bot'; self.color = "orange"
        self.energy_depletion_rate = 0.06
        
    def update(self, grid):
        """Player bot does not have autonomous AI."""
        if self.energy <= 0: return
        self.energy -= self.energy_depletion_rate; self.update_enhancements()