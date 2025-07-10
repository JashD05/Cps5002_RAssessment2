# agents/swarm.py
import math
import random
from agents.survivor_bot import SurvivorBot

class ScavengerSwarm:
    """A swarm that consumes parts, merges, and replicates."""
    def __init__(self, x, y, size=2):
        self.x = x
        self.y = y
        self.type = 'swarm'
        self.color = 'lawn green'
        self.size = size 
        # **FIX:** Increased damage radius and damage multiplier
        self.damage_field_radius = 2.0
        self.damage_per_size = 1.5 
        
        self.replication_threshold = 8 
        self.replication_chance = 0.02 

    def update(self, grid):
        """Main update logic for the swarm."""
        # 1. Damage nearby bots
        for bot in grid.get_all_bots():
            dist = math.hypot(self.x - bot.x, self.y - bot.y)
            if dist <= self.damage_field_radius and hasattr(bot, 'energy'):
                bot.energy -= self.size * self.damage_per_size

        # 2. Merge with other swarms
        for entity in grid.entities:
            if isinstance(entity, ScavengerSwarm) and entity is not self:
                if math.hypot(self.x - entity.x, self.y - entity.y) < 2:
                    self.merge(entity, grid)
                    return 

        # 3. Replicate if large enough
        if self.size >= self.replication_threshold and random.random() < self.replication_chance:
            self.replicate(grid)

        # 4. Move and consume parts
        self.move(grid)
        entity_at_pos = grid.get_entity(self.x, self.y)
        if entity_at_pos and entity_at_pos.type == 'spare_part':
            grid.remove_entity(entity_at_pos)
            self.size += 1

    def merge(self, other_swarm, grid):
        """Merges this swarm with another."""
        self.size += other_swarm.size
        grid.remove_entity(other_swarm)

    def replicate(self, grid):
        """Creates a new, smaller swarm nearby."""
        new_swarm_size = self.size // 2
        self.size -= new_swarm_size
        for _ in range(5):
            dx, dy = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
            new_x, new_y = self.x + dx, self.y + dy
            if grid.is_valid(new_x, new_y) and not grid.get_entity(new_x, new_y):
                new_swarm = ScavengerSwarm(new_x, new_y, size=new_swarm_size)
                grid.add_entity(new_swarm)
                return

    def move(self, grid):
        """Moves the swarm towards the nearest part, or randomly."""
        parts = [e for e in grid.entities if e.type == 'spare_part']
        closest_part = None
        if parts:
            closest_part = min(parts, key=lambda p: math.hypot(self.x-p.x, self.y-p.y))
        
        dx, dy = 0, 0
        if closest_part:
            if closest_part.x > self.x: dx = 1
            elif closest_part.x < self.x: dx = -1
            if closest_part.y > self.y: dy = 1
            elif closest_part.y < self.y: dy = -1
        else: 
            dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0), (0,0)])

        new_x, new_y = self.x + dx, self.y + dy
        if grid.is_valid(new_x, new_y):
             grid.move_entity(self, new_x, new_y)