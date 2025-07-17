# Techburg/agents/drone.py
import math, random
from agents.survivor_bot import SurvivorBot

class MalfunctioningDrone:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.type, self.color = 'drone', 'red'
        self.target_bot = None

    def update(self, grid):
        if not self.target_bot or self.target_bot not in grid.entities:
            bots = grid.get_all_bots()
            self.target_bot = min(bots, key=lambda b: math.hypot(self.x-b.x,self.y-b.y)) if bots else None
        if self.target_bot:
            if math.hypot(self.x-self.target_bot.x, self.y-self.target_bot.y) <= 1.5:
                self.target_bot.energy -= 50
                grid.log(f"[DRONE] Attacked {self.target_bot.bot_id}!")
            else: self.move_towards(self.target_bot, grid)
        else: self.move_randomly(grid)

    def move_towards(self, target, grid):
        dx = 1 if target.x > self.x else -1 if target.x < self.x else 0
        dy = 1 if target.y > self.y else -1 if target.y < self.y else 0
        grid.move_entity(self, self.x + dx, self.y + dy)
    def move_randomly(self, grid):
        dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
        grid.move_entity(self, self.x + dx, self.y + dy)