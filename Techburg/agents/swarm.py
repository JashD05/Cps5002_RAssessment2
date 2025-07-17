# Techburg/agents/swarm.py
import math, random

class ScavengerSwarm:
    def __init__(self, x, y, size=2):
        self.x, self.y, self.size = x, y, size
        self.type, self.color = 'swarm', 'lawn green'

    def update(self, grid):
        self.move(grid)
        entity = grid.get_entity(self.x, self.y)
        if entity and entity.type == 'spare_part':
            grid.remove_entity(entity); self.size += 1
            grid.log(f"[SWARM] Consumed a part at ({self.x},{self.y}). Size is now {self.size}.")

    def move(self, grid):
        dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
        grid.move_entity(self, self.x + dx, self.y + dy)