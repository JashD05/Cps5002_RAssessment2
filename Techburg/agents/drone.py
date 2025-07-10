# Techburg/agents/drone.py
import math
import random
from agents.survivor_bot import SurvivorBot

class MalfunctioningDrone:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type, self.color = 'drone', 'red'
        self.vision_range = 10
        self.attack_cooldown = 0
        self.shock_damage = 30
        self.disable_damage = 60
        self.target_bot = None

    def update(self, grid):
        if self.attack_cooldown > 0: self.attack_cooldown -= 1; return
        
        adjacent_bots = [b for b in grid.get_all_bots() if math.hypot(self.x-b.x, self.y-b.y) <= 1.5]
        if adjacent_bots:
            self.attack(self.prioritize_target(adjacent_bots))
            return

        if not self.target_bot or self.target_bot not in grid.entities:
            visible_bots = [b for b in grid.get_all_bots() if math.hypot(self.x-b.x, self.y-b.y) <= self.vision_range]
            self.target_bot = self.prioritize_target(visible_bots) if visible_bots else None
        
        if self.target_bot:
            self.move_towards(self.target_bot, grid)
        else:
            self.move_randomly(grid)

    def prioritize_target(self, bots):
        player = next((b for b in bots if b.type == 'player_bot'), None)
        if player: return player
        part_carrier = next((b for b in bots if hasattr(b, 'carrying_part') and b.carrying_part), None)
        if part_carrier: return part_carrier
        return min(bots, key=lambda b: math.hypot(self.x-b.x, self.y-b.y))
        
    def move_towards(self, target, grid):
        """Moves one step directly towards the target."""
        dx, dy = 0, 0
        if target.x > self.x: dx = 1
        elif target.x < self.x: dx = -1
        if target.y > self.y: dy = 1
        elif target.y < self.y: dy = -1
        new_x, new_y = self.x + dx, self.y + dy
        grid.move_entity(self, new_x, new_y)

    def attack(self, bot):
        is_high_priority = bot.type == 'player_bot' or (hasattr(bot, 'carrying_part') and bot.carrying_part)
        if is_high_priority:
            bot.energy -= self.disable_damage; bot.stunned = 2
        else:
            bot.energy -= self.shock_damage; bot.stunned = 1
        self.attack_cooldown = 3
    
    def move_randomly(self, grid):
        moves = [(0,1),(0,-1),(1,0),(-1,0)]; random.shuffle(moves)
        for dx, dy in moves:
            new_x, new_y = self.x+dx, self.y+dy
            if grid.is_valid(new_x,new_y) and not grid.get_entity(new_x,new_y):
                grid.move_entity(self,new_x,new_y); return