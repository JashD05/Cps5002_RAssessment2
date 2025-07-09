# File: Techburg/agents/swarm.py
import math

class ScavengerSwarm:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = "swarm"
        self.color = "lawn green"
        # HARD MODE: Swarms have a damaging aura
        self.decay_field_radius = 1.5 # Adjacent cells, including diagonals
        self.decay_damage = 5

    def update(self, grid):
        """Swarm AI: Move randomly, consume parts, and damage nearby bots."""
        import random

        # --- HARD MODE: Decay Field Logic ---
        for bot in grid.get_all_bots():
            dist = math.hypot(self.x - bot.x, self.y - bot.y)
            if dist <= self.decay_field_radius:
                # This bot is adjacent to the swarm
                bot.energy -= self.decay_damage
        # --- End Decay Field Logic ---

        # Move to a new random location
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = (self.x + dx) % grid.width
        new_y = (self.y + dy) % grid.height
        
        if grid.move_entity(self, new_x, new_y):
            # After moving, check for parts to consume
            entity_at_pos = grid.get_entity(self.x, self.y)
            if entity_at_pos and entity_at_pos.type == 'spare_part':
                grid.remove_entity(entity_at_pos)