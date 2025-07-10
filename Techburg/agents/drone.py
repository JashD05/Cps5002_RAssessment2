# agents/drone.py
import math
import random
from ai.pathfinding import find_path
from agents.survivor_bot import SurvivorBot

class MalfunctioningDrone:
    """A drone that hunts and attacks survivor bots strategically."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 100
        self.path = []
        self.type = 'drone'
        self.color = 'red'
        self.vision_range = 8
        self.attack_cooldown = 0
        # **FIX:** Increased damage values to make drones more dangerous
        self.shock_damage = 25
        self.disable_damage = 50

    def update(self, grid):
        """Main update logic for the drone."""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            return

        # Check for adjacent bots to attack
        adjacent_bots = [b for b in grid.get_all_bots() if math.hypot(self.x - b.x, self.y - b.y) <= 1.5]
        if adjacent_bots:
            target = self.prioritize_target(adjacent_bots)
            self.attack(target, grid)
            return

        # If no path, find a target
        if not self.path or not self.path_target_is_valid(grid):
            visible_bots = [b for b in grid.get_all_bots() if math.hypot(self.x - b.x, self.y - b.y) <= self.vision_range]
            if visible_bots:
                target = self.prioritize_target(visible_bots)
                self.path = find_path(grid, (self.x, self.y), (target.x, target.y))
            else:
                self.move_randomly(grid)
                return
        
        # Move along the path
        if self.path:
            next_pos = self.path.pop(0)
            grid.move_entity(self, next_pos[0], next_pos[1])

    def path_target_is_valid(self, grid):
        if not self.path: return False
        end_pos = self.path[-1]
        target_entity = grid.get_entity(end_pos[0], end_pos[1])
        return target_entity and isinstance(target_entity, SurvivorBot)

    def prioritize_target(self, bots):
        """Prioritizes player bots or bots carrying parts."""
        player = next((b for b in bots if b.type == 'player_bot'), None)
        if player: return player
        
        part_carrier = next((b for b in bots if hasattr(b, 'carrying_part') and b.carrying_part), None)
        if part_carrier: return part_carrier
        
        return min(bots, key=lambda b: math.hypot(self.x - b.x, self.y - b.y))

    def attack(self, bot, grid):
        """Decides which attack to use based on the target."""
        is_high_priority = bot.type == 'player_bot' or (hasattr(bot, 'carrying_part') and bot.carrying_part)
        
        if is_high_priority:
            bot.energy -= self.disable_damage
            if hasattr(bot, 'stunned'): bot.stunned = 2
            self.attack_cooldown = 5
        else: 
            bot.energy -= self.shock_damage
            if hasattr(bot, 'stunned'): bot.stunned = 1
            self.attack_cooldown = 3
    
    def move_randomly(self, grid):
        """Moves the drone to a random adjacent tile."""
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(moves)
        for dx, dy in moves:
            new_x, new_y = self.x + dx, self.y + dy
            if grid.is_valid(new_x, new_y) and not grid.get_entity(new_x, new_y):
                 grid.move_entity(self, new_x, new_y)
                 return