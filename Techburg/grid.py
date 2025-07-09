# File: grid.py

from typing import Tuple, List, Any

class Grid:
    def __init__(self, size: Tuple[int, int]):
        self.width, self.height = size
        self.bots: List[Any] = []
        self.drones: List[Any] = []
        self.swarms: List[Any] = []
        self.parts: List[Any] = []
        self.stations: List[Tuple[int, int]] = []

    def get_all_entities(self) -> List[Any]:
        return self.bots + self.drones + self.swarms + self.parts

    def get_all_threats(self) -> List[Any]:
        return self.drones + self.swarms

    def get_drawable_stations(self) -> List[Any]:
        return [type('obj', (object,), {'position': s, 'color': 'purple'}) for s in self.stations]

    def wrap_position(self, position: Tuple[int, int]) -> Tuple[int, int]:
        x, y = position
        return (x % self.width, y % self.height)