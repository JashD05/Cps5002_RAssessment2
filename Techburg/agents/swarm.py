# Techburg/agents/swarm.py
import math
import random

class ScavengerSwarm:
    def __init__(self, x, y, size=2):
        self.x, self.y, self.size = x, y, size
        self.type, self.color = 'swarm', 'lawn green'
        self.damage_field_radius, self.damage_per_size = 2.5, 2.5
        self.replication_threshold, self.replication_chance = 8, 0.02

    def update(self, grid):
        for bot in grid.get_all_bots():
            if math.hypot(self.x-bot.x, self.y-bot.y) <= self.damage_field_radius:
                damage = self.size * self.damage_per_size
                if hasattr(bot, 'energy'): bot.energy -= damage
                grid.log(f"[DAMAGE] Swarm dealt {int(damage)} damage to {getattr(bot, 'bot_id', 'a bot')}.")
        
        for entity in grid.entities:
            if isinstance(entity,ScavengerSwarm) and entity is not self and math.hypot(self.x-entity.x, self.y-entity.y) < 2:
                grid.log(f"[EVENT] Swarms merged! New size: {self.size + entity.size}")
                self.size += entity.size; grid.remove_entity(entity); return
        
        if self.size >= self.replication_threshold and random.random() < self.replication_chance:
            self.replicate(grid)
        
        self.move(grid)
        entity_at_pos = grid.get_entity(self.x, self.y)
        if entity_at_pos and entity_at_pos.type == 'spare_part':
            grid.log(f"[EVENT] Swarm consumed a part and grew to size {self.size + 1}.")
            grid.remove_entity(entity_at_pos); self.size += 1

    def replicate(self, grid):
        new_swarm_size = self.size // 2; self.size -= new_swarm_size
        for _ in range(5):
            dx, dy = random.choice([(1,0),(-1,0),(0,1),(-1,0)])
            new_x, new_y = self.x+dx, self.y+dy
            if grid.is_valid(new_x,new_y) and not grid.get_entity(new_x,new_y):
                grid.log(f"[EVENT] Swarm at ({self.x}, {self.y}) replicated!")
                grid.add_entity(ScavengerSwarm(new_x, new_y, size=new_swarm_size)); return

    def move(self, grid):
        parts = [e for e in grid.entities if e.type == 'spare_part']
        closest_part = min(parts, key=lambda p: math.hypot(self.x-p.x, self.y-p.y)) if parts else None
        
        dx, dy = 0, 0
        if closest_part:
            if closest_part.x > self.x: dx=1
            elif closest_part.x < self.x: dx=-1
            if closest_part.y > self.y: dy=1
            elif closest_part.y < self.y: dy=-1
        else: dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
        
        new_x, new_y = self.x+dx, self.y+dy
        grid.move_entity(self, new_x, new_y)