# File: agents/survivor_bot.py

from typing import Tuple, Optional, List
from enum import Enum, auto
from ai.pathfinding import AStarPathfinder
from entities import SparePart

# --- NEW PERFORMANCE CONSTANT ---
# Bots will only consider parts within this distance.
# This dramatically reduces CPU and Memory usage.
MAX_AI_SCAVENGE_RADIUS = 15

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
            self._start_moving_to_station(grid)
            return
        if not self.path:
            if self.state == BotState.MOVING_TO_PART: self._handle_arrival_at_part(grid)
            elif self.state == BotState.MOVING_TO_STATION: self._handle_arrival_at_station()
            else:
                self.state = BotState.SEARCHING
                self._search_for_best_part(grid)

    def move(self, grid):
        if self.path:
            self.position = self.path.pop(0)
            self.energy -= 5
            self.position = grid.wrap_position(self.position)

    def _handle_arrival_at_part(self, grid):
        self.carried_part, self.target_part = self.target_part, None
        if self.carried_part in grid.parts: grid.parts.remove(self.carried_part)
        self._start_moving_to_station(grid)

    def _handle_arrival_at_station(self):
        if self.carried_part: self.carried_part = None
        self.energy = min(100, self.energy + 10.0)
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

    def _search_for_best_part(self, grid):
        """Finds the best part, but now only considers nearby parts."""
        if not grid.parts: return
        
        # --- PERFORMANCE OPTIMIZATION ---
        # First, filter for parts within the bot's "scavenge radius".
        nearby_parts = [
            p for p in grid.parts
            if self.pathfinder._get_heuristic(self.position, p.position) <= MAX_AI_SCAVENGE_RADIUS
        ]
        if not nearby_parts: return # No parts are close enough to consider.

        threats = grid.get_all_threats()
        self.pathfinder.update_obstacles([t.position for t in threats])
        
        # Now, only score the nearby parts.
        scored_parts = [(p, self._score_part(p, threats)) for p in nearby_parts]
        if not scored_parts: return
        
        self.target_part, _ = max(scored_parts, key=lambda item: item[1])
        path_result = self.pathfinder.find_path(self.position, self.target_part.position)
        if path_result:
            self.path, self.state = path_result[1:], BotState.MOVING_TO_PART

    def _start_moving_to_station(self, grid):
        if not grid.stations: return
        station_positions = [s.position for s in grid.stations]
        closest = min(station_positions, key=lambda s: self.pathfinder._get_heuristic(self.position, s))
        path_result = self.pathfinder.find_path(self.position, closest)
        if path_result:
            self.path, self.state = path_result[1:], BotState.MOVING_TO_STATION

class GathererBot(SurvivorBot):
    """A bot specialized in gathering parts."""
    def __init__(self, bot_id: int, start_pos: Tuple[int, int], pathfinder: AStarPathfinder):
        super().__init__(bot_id, start_pos, pathfinder)
        self.color = "light sea green"

class RepairBot(SurvivorBot):
    """A bot specialized in repairing and enabling replication."""
    def __init__(self, bot_id: int, start_pos: Tuple[int, int], pathfinder: AStarPathfinder):
        super().__init__(bot_id, start_pos, pathfinder)
        self.color = "cornflower blue"

class PlayerBot(SurvivorBot):
    """A SurvivorBot controlled by the player's keyboard input."""
    def __init__(self, bot_id: int, start_pos: Tuple[int, int], pathfinder: AStarPathfinder):
        super().__init__(bot_id, start_pos, pathfinder)
        self.color = "orange"
        self.speed_enhancement = 0
        self.vision_enhancement = 0
        self.energy_capacity = 100
        
    def think(self, grid): pass
    def move(self, grid): pass