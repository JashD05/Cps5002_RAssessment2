# File: agents/swarm.py

import random
from typing import List
from entities import SparePart

class ScavengerSwarm:
    def __init__(self, position):
        self.position = position
        self.size = 1
        self.color = "green"

    def act(self, all_entities: List, parts: List[SparePart]):
        self._apply_decay_field(all_entities)
        self._consume(all_entities, parts)
        self._move()

    def _apply_decay_field(self, all_entities: List):
        for entity in all_entities:
            if hasattr(entity, 'energy'):
                distance = abs(self.position[0] - entity.position[0]) + abs(self.position[1] - entity.position[1])
                if distance <= 1 and entity != self:
                    entity.energy -= 3.0 # [cite: 87]

    def _consume(self, all_entities: List, parts: List[SparePart]):
        item_to_remove = next((item for item in all_entities if self.position == item.position and item != self and item in parts), None)
        if item_to_remove:
            parts.remove(item_to_remove)
            all_entities.remove(item_to_remove)
    
    def _move(self):
        dx, dy = random.choice([-1, 0, 1]), random.choice([-1, 0, 1])
        self.position = ((self.position[0] + dx) % 30, (self.position[1] + dy) % 30)