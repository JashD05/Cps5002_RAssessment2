# File: agents/drone.py

import random
from enum import Enum, auto
from typing import List
from agents.survivor_bot import SurvivorBot

class DroneState(Enum):
    PATROLLING = auto()
    PURSUING = auto()
    HIBERNATING = auto()

class MalfunctioningDrone:
    def __init__(self, position):
        self.position = position
        self.energy = 100.0
        self.state = DroneState.PATROLLING
        self.target_bot = None
        self.color = "red"

    def act(self, bots: List[SurvivorBot]):
        if self.state == DroneState.HIBERNATING: self._handle_hibernating()
        elif self.state == DroneState.PURSUING: self._handle_pursuing(bots)
        else: self._handle_patrolling(bots)

    def _handle_hibernating(self):
        # [cite_start]
        self.energy += 10.0 # [cite: 80]
        if self.energy >= 100:
            self.energy = 100
            self.state = DroneState.PATROLLING

    def _handle_patrolling(self, bots: List[SurvivorBot]):
        for bot in bots:
            distance = abs(self.position[0] - bot.position[0]) + abs(self.position[1] - bot.position[1])
            # [cite_start]
            if distance <= 3: # [cite: 74]
                self.target_bot = bot
                self.state = DroneState.PURSUING
                return
        
        dx, dy = random.choice([-1, 0, 1]), random.choice([-1, 0, 1])
        self.position = ((self.position[0] + dx) % 30, (self.position[1] + dy) % 30)

    def _handle_pursuing(self, bots: List[SurvivorBot]):
        if not self.target_bot or self.target_bot not in bots:
            self.state, self.target_bot = DroneState.PATROLLING, None
            return

        self.energy -= 1.0 # Simplified pursuit energy cost
        # [cite_start]
        if self.energy <= 20: # [cite: 80]
            self.state = DroneState.HIBERNATING
            return

        if self.position == self.target_bot.position:
            self._attack(self.target_bot)
        else:
            dx = self.target_bot.position[0] - self.position[0]
            dy = self.target_bot.position[1] - self.position[1]
            self.position = ((self.position[0] + (1 if dx > 0 else -1 if dx < 0 else 0)) % 30, (self.position[1] + (1 if dy > 0 else -1 if dy < 0 else 0)) % 30)

    def _attack(self, bot: SurvivorBot):
        attack_type = random.choice(["shock", "disable"])
        # [cite_start]
        if attack_type == "shock": bot.energy -= 5.0 # [cite: 77]
        else: bot.energy -= 20.0 # [cite: 77]
        # [cite_start]
        if bot.carried_part: bot.carried_part = None # [cite: 77]