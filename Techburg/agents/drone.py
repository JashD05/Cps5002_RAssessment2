# Techburg/agents/drone.py
import math, random
from ai.pathfinding import find_path
from agents.survivor_bot import SurvivorBot

class MalfunctioningDrone:
    def __init__(self, x, y):
        self.x, self.y = x, y; self.path = []
        self.type, self.color = 'drone', 'red'
        self.vision_range = 10; self.attack_cooldown = 0
        self.shock_damage, self.disable_damage = 30, 60
        self.energy = 500; self.energy_depletion_rate = 0.1

    def update(self, grid):
        if self.energy <= 0: grid.remove_entity(self); return
        self.energy -= self.energy_depletion_rate
        if self.attack_cooldown > 0: self.attack_cooldown -= 1; return
        adjacent_bots = [b for b in grid.get_all_bots() if math.hypot(self.x-b.x, self.y-b.y) <= 1.5]
        if adjacent_bots: self.attack(self.prioritize_target(adjacent_bots), grid); return
        if not self.path:
            visible_bots = [b for b in grid.get_all_bots() if math.hypot(self.x-b.x, self.y-b.y) <= self.vision_range]
            if visible_bots:
                target = self.prioritize_target(visible_bots)
                self.path = find_path(grid, (self.x, self.y), (target.x, target.y))
            else: self.move_randomly(grid); return
        if self.path:
            try: next_pos = self.path.pop(0); grid.move_entity(self, next_pos[0], next_pos[1]); self.energy -= 0.5
            except IndexError: self.path = []

    def prioritize_target(self, bots):
        player = next((b for b in bots if b.type == 'player_bot'), None)
        if player: return player
        part_carrier = next((b for b in bots if b.carrying_part), None)
        if part_carrier: return part_carrier
        return min(bots, key=lambda b: math.hypot(self.x-b.x, self.y-b.y))

    def attack(self, bot, grid):
        is_high_priority = bot.type == 'player_bot' or bot.carrying_part
        if is_high_priority:
            attack_type, damage = "DISABLE", self.disable_damage; bot.energy -= damage; bot.stunned = 2
        else:
            attack_type, damage = "SHOCK", self.shock_damage; bot.energy -= damage; bot.stunned = 1
        grid.log(f"[ATTACK] Drone used {attack_type} on {bot.bot_id} for {damage} damage.")
        self.attack_cooldown = 3
    
    def move_randomly(self, grid):
        moves = [(0,1),(0,-1),(1,0),(-1,0)]; random.shuffle(moves)
        for dx, dy in moves:
            new_x, new_y = self.x+dx, self.y+dy
            if grid.is_valid(new_x,new_y) and not grid.get_entity(new_x,new_y): grid.move_entity(self,new_x,new_y); return