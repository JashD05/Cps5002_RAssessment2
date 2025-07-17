# Techburg/agents/swarm.py
import math, random

class ScavengerSwarm:
    def __init__(self, x, y, size=2):
        self.x, self.y, self.size = x, y, size
        self.type, self.color = 'swarm', 'lawn green'
        self.damage_radius = 1.5

    def update(self, grid):
        for bot in grid.get_all_bots():
            if math.hypot(self.x-bot.x, self.y-bot.y) <= self.damage_radius:
                damage = self.size * 2
                bot.energy -= damage
                grid.log(f"[SWARM] Dealt {damage} decay damage to {bot.bot_id}.")

        self.move(grid)
        entity = grid.get_entity(self.x, self.y)
        if entity and entity.type == 'spare_part':
            grid.remove_entity(entity); self.size += 1
            grid.log(f"[SWARM] Consumed a part at ({self.x},{self.y}). Size is now {self.size}.")

    def move(self, grid):
        dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
        grid.move_entity(self, self.x + dx, self.y + dy)