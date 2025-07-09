# File: Techburg/agents/drone.py
import math
from ai.pathfinding import find_path

class MalfunctioningDrone:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = 100
        self.path = []
        self.type = "drone"
        self.color = "red"
        # HARD MODE: Drones can see further
        self.vision_range = 5
        self.attack_damage = 15

    def update(self, grid):
        """Drone AI: find closest bot, move towards it, and attack if adjacent."""

        # --- HARD MODE: Attack Logic ---
        # Check for adjacent bots to attack
        for bot in grid.get_all_bots():
            dist = math.hypot(self.x - bot.x, self.y - bot.y)
            if dist <= 1.5: # If adjacent (including diagonals)
                print(f"Drone at ({self.x}, {self.y}) shocked Bot {bot.bot_id}!")
                bot.energy -= self.attack_damage
                # Drone stops moving for one turn after attacking
                return
        # --- End Attack Logic ---

        if self.path:
            next_pos = self.path.pop(0)
            grid.move_entity(self, next_pos[0], next_pos[1])
            return

        # Find the nearest bot within vision range
        nearby_bots = [b for b in grid.get_all_bots() if math.hypot(self.x - b.x, self.y - b.y) <= self.vision_range]
        if nearby_bots:
            target = min(nearby_bots, key=lambda b: math.hypot(self.x - b.x, self.y - b.y))
            path = find_path(grid, (self.x, self.y), (target.x, target.y))
            if path: self.path = path
        else:
            self.move_randomly(grid)

    def move_randomly(self, grid):
        import random
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = (self.x + dx) % grid.width
        new_y = (self.y + dy) % grid.height
        grid.move_entity(self, new_x, new_y)