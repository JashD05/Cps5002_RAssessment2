# File: agents/swarm.py
import random
from entities import SparePart

class ScavengerSwarm:
    def __init__(self, position):
        self.position = position
        self.color = "lawn green"

    def think(self, grid):
        self._apply_decay_field(grid.bots + grid.drones)
        self._consume(grid)

    def move(self, grid):
        self.position = (self.position[0] + random.choice([-1, 0, 1]), self.position[1] + random.choice([-1, 0, 1]))
        self.position = grid.wrap_position(self.position)

    def _apply_decay_field(self, agents):
        for agent in agents:
            dist = abs(self.position[0] - agent.position[0]) + abs(self.position[1] - agent.position[1])
            if dist <= 1: agent.energy = max(0, agent.energy - 3.0)

    def _consume(self, grid):
        item_to_remove = next((part for part in grid.parts if self.position == part.position), None)
        if item_to_remove:
            grid.parts.remove(item_to_remove)