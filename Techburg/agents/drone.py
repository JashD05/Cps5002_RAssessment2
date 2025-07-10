# Techburg/agents/drone.py
import math
import random
# Corrected: Import is now relative to the Techburg directory.
from ai.pathfinding import find_path

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
        self.shock_damage = 10
        self.disable_damage = 25

    def update(self, grid):
        """Main update logic for the drone."""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            return

        adjacent_bots = [b for b in grid.get_all_bots() if math.hypot(self.x - b.x, self.y - b.y) <= 1.5]
        if adjacent_bots:
            target = self.prioritize_target(adjacent_bots)
            self.attack(target, grid)
            return

        if not self.path:
            visible_bots = [b for b in grid.get_all_bots() if math.hypot(self.x - b.x, self.y - b.y) <= self.vision_range]
            if visible_bots:
                target = self.prioritize_target(visible_bots)
                path_to_target = find_path(grid, (self.x, self.y), (target.x, target.y))
                if path_to_target:
                    self.path = path_to_target
            else:
                self.move_randomly(grid)
                return
        
        if self.path:
            next_pos = self.path.pop(0)
            entity_at_next_pos = grid.get_entity(next_pos[0], next_pos[1])
            if not entity_at_next_pos or entity_at_next_pos.type in ['player_bot', 'gatherer_bot', 'repair_bot', 'survivor_bot', 'spare_part']:
                 grid.move_entity(self, next_pos[0], next_pos[1])
            else:
                self.path = []

    def prioritize_target(self, bots):
        """Prioritizes player bots or bots carrying parts."""
        for bot in bots:
            if bot.type == 'player_bot':
                return bot
        for bot in bots:
            if hasattr(bot, 'carrying_part') and bot.carrying_part:
                return bot
        return min(bots, key=lambda b: math.hypot(self.x - b.x, self.y - b.y))

    def attack(self, bot, grid):
        """Decides which attack to use based on the target."""
        is_high_priority = bot.type == 'player_bot' or (hasattr(bot, 'carrying_part') and bot.carrying_part)
        
        if is_high_priority:
            bot.energy -= self.disable_damage
            if hasattr(bot, 'stunned'):
                bot.stunned = 2
            self.attack_cooldown = 5
            print(f"Drone used DISABLE on {bot.type} at ({bot.x}, {bot.y})!")
        else:
            bot.energy -= self.shock_damage
            if hasattr(bot, 'stunned'):
                bot.stunned = 1
            self.attack_cooldown = 3
            print(f"Drone SHOCKED {bot.type} at ({bot.x}, {bot.y})!")
    
    def move_randomly(self, grid):
        """Moves the drone to a random adjacent tile."""
        moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(moves)
        for dx, dy in moves:
            new_x, new_y = (self.x + dx, self.y + dy)
            if grid.is_valid(new_x, new_y) and not grid.get_entity(new_x, new_y):
                 grid.move_entity(self, new_x, new_y)
                 return