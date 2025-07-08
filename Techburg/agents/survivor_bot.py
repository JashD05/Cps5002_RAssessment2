# File: agents/survivor_bot.py

from typing import Tuple, Optional, List
from enum import Enum, auto
from ai.pathfinding import AStarPathfinder
from entities import SparePart

class BotState(Enum):
    SEARCHING = auto()
    MOVING_TO_PART = auto()
    MOVING_TO_STATION = auto()

class SurvivorBot:
    def __init__(self, bot_id: int, start_pos: Tuple[int, int], pathfinder: AStarPathfinder):
        self.id = bot_id
        self.position = start_pos
        self.pathfinder = pathfinder
        self.energy = 100.0
        self.state = BotState.SEARCHING
        self.path: List[Tuple[int, int]] = []
        self.carried_part: Optional[SparePart] = None
        self.target_part: Optional[SparePart] = None
        self.color = "blue"

    def act(self, parts: List[SparePart], stations: List[Tuple[int, int]], threats: List):
        if self.state == BotState.SEARCHING:
            self._handle_searching_state(parts, threats)
        elif self.state == BotState.MOVING_TO_PART:
            self._handle_moving_to_part(parts)
        elif self.state == BotState.MOVING_TO_STATION:
            self._handle_moving_to_station(stations)
        
        if self.energy <= 40 and self.state != BotState.MOVING_TO_STATION:
            print(f"Bot {self.id}: Energy low ({self.energy:.1f}%)! Returning to station.")
            self.carried_part = None
            self._plan_path_to_nearest_station(stations)

    def _score_part(self, part: SparePart, threats: List) -> float:
        VALUE_WEIGHT, DISTANCE_WEIGHT, RISK_WEIGHT = 1.5, 1.0, 2.0
        value_score = part.enhancement_value
        distance_to_part = self.pathfinder._get_heuristic(self.position, part.position)
        risk_penalty = 0
        if threats:
            min_dist_to_threat = min([self.pathfinder._get_heuristic(part.position, t.position) for t in threats])
            if min_dist_to_threat <= 3:
                risk_penalty = 10
        return (value_score * VALUE_WEIGHT) - (distance_to_part * DISTANCE_WEIGHT) - (risk_penalty * RISK_WEIGHT)

    def _handle_searching_state(self, parts: List[SparePart], threats: List):
        if not parts: return
        current_threat_positions = [t.position for t in threats]
        self.pathfinder.update_obstacles(current_threat_positions)
        
        scored_parts = [(p, self._score_part(p, threats)) for p in parts]
        if not scored_parts: return
        
        best_part, _ = max(scored_parts, key=lambda item: item[1])
        self.target_part = best_part
        
        path_result = self.pathfinder.find_path(self.position, self.target_part.position)
        if path_result:
            self.path = path_result[1:]
            self.state = BotState.MOVING_TO_PART

    def _handle_moving_to_part(self, parts: List[SparePart]):
        if not self.target_part or self.target_part not in parts:
            self.state = BotState.SEARCHING
            return

        if self.position == self.target_part.position:
            self.carried_part = self.target_part # [cite: 46]
            parts.remove(self.carried_part)
            self.state = BotState.MOVING_TO_STATION
            self.path = []
            self.target_part = None
        else:
            self._move_along_path()

    def _handle_moving_to_station(self, stations: List[Tuple[int, int]]):
        if not self.path: self._plan_path_to_nearest_station(stations)
        
        if self.position in stations:
            if self.carried_part: self.carried_part = None
            self.energy += 1.0 # [cite: 52]
            if self.energy > 100: self.energy = 100
            if self.energy == 100: self.state = BotState.SEARCHING
        else:
            self._move_along_path()

    def _plan_path_to_nearest_station(self, stations: List[Tuple[int, int]]):
        if not stations: return
        closest_station = min(stations, key=lambda s: self.pathfinder._get_heuristic(self.position, s))
        path_result = self.pathfinder.find_path(self.position, closest_station)
        if path_result:
            self.path = path_result[1:]
            self.state = BotState.MOVING_TO_STATION

    def _move_along_path(self):
        if self.path:
            self.position = self.path.pop(0)
            self.energy -= 5 # [cite: 47]
        else:
            self.state = BotState.SEARCHING