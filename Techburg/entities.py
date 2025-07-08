# File: entities.py

from enum import Enum, auto

class PartSize(Enum):
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()

class SparePart:
    """Represents a spare part in the simulation."""
    def __init__(self, position, size: PartSize):
        self.position = position
        self.size = size
        self.enhancement_value = self._get_initial_value()
        self.color = self._get_color()

    def _get_initial_value(self) -> float:
        if self.size == PartSize.SMALL:
            return 3.0 # [cite: 37]
        elif self.size == PartSize.MEDIUM:
            return 5.0 # [cite: 37]
        elif self.size == PartSize.LARGE:
            return 7.0 # [cite: 37]
        return 0.0

    def _get_color(self) -> str:
        if self.size == PartSize.SMALL:
            return "cyan"
        elif self.size == PartSize.MEDIUM:
            return "magenta"
        return "yellow"

    def corrode(self):
        """Reduces the part's value each simulation step."""
        if self.enhancement_value > 0:
            self.enhancement_value -= 0.1 # [cite: 38]