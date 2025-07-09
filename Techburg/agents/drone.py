# File: agents/drone.py
import random
from enum import Enum, auto

class DroneState(Enum):
    PATROLLING, PURSUING, HIBERNATING = auto(), auto(), auto()

class MalfunctioningDrone:
    def __init__(self, position):
        self.position, self.energy = position, 100.0
        self.state, self.target_bot = DroneState.PATROLLING, None
        self.color = "red"

    def think(self, grid):
        if self.energy <= 20: self.state = DroneState.HIBERNATING
        elif self.state == DroneState.PATROLLING:
            for bot in grid.bots:
                dist = abs(self.position[0] - bot.position[0]) + abs(self.position[1] - bot.position[1])
                if dist <= 3:
                    self.target_bot, self.state = bot, DroneState.PURSUING
                    return
        elif self.state == DroneState.PURSUING and (not self.target_bot or self.target_bot not in grid.bots):
             self.state, self.target_bot = DroneState.PATROLLING, None

    def move(self, grid):
        if self.state == DroneState.HIBERNATING:
            self.energy = min(100, self.energy + 10.0)
            if self.energy == 100: self.state = DroneState.PATROLLING
        elif self.state == DroneState.PATROLLING:
            self.position = (self.position[0] + random.choice([-1, 0, 1]), self.position[1] + random.choice([-1, 0, 1]))
        elif self.state == DroneState.PURSUING:
            self.energy -= 1.0
            if self.position == self.target_bot.position: self._attack(self.target_bot)
            else:
                dx = self.target_bot.position[0] - self.position[0]
                dy = self.target_bot.position[1] - self.position[1]
                self.position = (self.position[0] + (1 if dx > 0 else -1 if dx < 0 else 0), self.position[1] + (1 if dy > 0 else -1 if dy < 0 else 0))
        self.position = grid.wrap_position(self.position)

    def _attack(self, bot):
        if random.random() < 0.5: bot.energy -= 5.0
        else: bot.energy -= 20.0
        if bot.carried_part: bot.carried_part = None