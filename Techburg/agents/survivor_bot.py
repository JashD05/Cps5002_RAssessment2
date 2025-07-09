# File: agents/survivor_bot.py

from typing import Tuple, Optional, List
from enum import Enum, auto
from ai.pathfinding import AStarPathfinder
from entities import SparePart

class BotState(Enum):
    SEARCHING, MOVING_TO_PART, MOVING_TO_STATION = auto(), auto(), auto()

class SurvivorBot:
    def __init__(self, bot_id: int, start_pos: Tuple[int, int], pathfinder: AStarPathfinder):
        self.id, self.position, self.pathfinder = bot_id, start_pos, pathfinder
        self.energy, self.state = 100.0, BotState.SEARCHING
        self.path: List[Tuple[int, int]] = []
        self.carried_part: Optional[SparePart] = None
        self.target_part: Optional[SparePart] = None
        self.color = "deep sky blue"

    def think(self, grid):
        if self.energy <= 40 and self.state != BotState.MOVING_TO_STATION:
            self.carried_part, self.target_part, self.path = None, None, []
            self._plan_path_to_nearest_station(grid)
            return
        if self.state == BotState.SEARCHING:
            self._handle_searching_state(grid)
        elif self.position in grid.stations and self.state == BotState.MOVING_TO_STATION:
            self._handle_at_station()

    def move(self, grid):
        if self.path:
            self.position = self.path.pop(0)
            self.energy -= 5
            self.position = grid.wrap_position(self.position)
            if self.state == BotState.MOVING_TO_PART and self.position == self.target_part.position:
                self._handle_arrival_at_part(grid)
        elif self.state != BotState.SEARCHING:
            self.state = BotState.SEARCHING

    def _handle_arrival_at_part(self, grid):
        self.carried_part, self.state = self.target_part, BotState.MOVING_TO_STATION
        if self.target_part in grid.parts:
            grid.parts.remove(self.target_part)
        self.path, self.target_part = [], None
        self._plan_path_to_nearest_station(grid)

    def _handle_at_station(self):
        if self.carried_part: self.carried_part = None
        self.energy = min(100, self.energy + 1.0)
        if self.energy == 100: self.state = BotState.SEARCHING
    
    def _score_part(self, part: SparePart, threats: List) -> float:
        VALUE_WEIGHT, DISTANCE_WEIGHT, RISK_WEIGHT = 1.5, 1.0, 2.0
        value = part.enhancement_value
        distance = self.pathfinder._get_heuristic(self.position, part.position)
        risk = 0
        if threats:
            min_dist = min([self.pathfinder._get_heuristic(part.position, t.position) for t in threats])
            if min_dist <= 3: risk = 10
        return (value * VALUE_WEIGHT) - (distance * DISTANCE_WEIGHT) - (risk * RISK_WEIGHT)

    def _handle_searching_state(self, grid):
        if not grid.parts: return
        threats = grid.get_all_threats()
        self.pathfinder.update_obstacles([t.position for t in threats])
        scored_parts = [(p, self._score_part(p, threats)) for p in grid.parts]
        if not scored_parts: return
        self.target_part, _ = max(scored_parts, key=lambda item: item[1])
        path_result = self.pathfinder.find_path(self.position, self.target_part.position)
        if path_result:
            self.path, self.state = path_result[1:], BotState.MOVING_TO_PART

    def _plan_path_to_nearest_station(self, grid):
        if not grid.stations: return
        closest = min(grid.stations, key=lambda s: self.pathfinder._get_heuristic(self.position, s))
        path_result = self.pathfinder.find_path(self.position, closest)
        if path_result:
            self.path, self.state = path_result[1:], BotState.MOVING_TO_STATION