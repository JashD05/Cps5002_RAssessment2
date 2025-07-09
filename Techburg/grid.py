# File: grid.py
import random
import heapq # For A* pathfinding
from entities import PlayerBot, GathererBot, RepairBot, MalfunctioningDrone, ScavengerSwarm, SparePart, RechargeStation

class Grid:
    """
    Represents the 2D world of Techburg, managing all entities and pathfinding.
    """
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Use a dictionary for faster lookups of entities at a specific coordinate
        self.grid = {}
        # A list to hold all entity objects for easy iteration
        self.entities = []
        # Statistics tracking
        self._initial_parts_count = 0
        self._parts_collected_count = 0
        self._bots_destroyed_count = 0

    def add_entity(self, entity):
        """Adds an entity to a specific location in the grid and to the entity list."""
        self.grid[(entity.x, entity.y)] = entity
        self.entities.append(entity)
        if "part" in entity.type:
            self._initial_parts_count += 1

    def move_entity(self, entity, new_x, new_y):
        """Moves an entity from its current position to a new one."""
        # Check if the destination is empty
        if self.grid.get((new_x, new_y)) is None:
            # Remove from old position
            del self.grid[(entity.x, entity.y)]
            # Add to new position
            self.grid[(new_x, new_y)] = entity
            # Update entity's own coordinates
            entity.x = new_x
            entity.y = new_y
            return True
        return False

    def remove_entity(self, entity):
        """Completely removes an entity from the simulation."""
        if (entity.x, entity.y) in self.grid:
            del self.grid[(entity.x, entity.y)]
        if entity in self.entities:
            self.entities.remove(entity)

    def get_entity(self, x, y):
        """Gets the entity at a specific location. Returns None if empty."""
        return self.grid.get((x, y))

    def get_random_empty_coords(self):
        """Finds a random empty cell in the grid."""
        while True:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (x, y) not in self.grid:
                return x, y

    def update_world(self):
        """Update all entities in the world for one simulation step."""
        for entity in list(self.entities): # Use a copy in case entities are removed during update
            if hasattr(entity, 'update'):
                entity.update(self)

    def populate_world(self, **kwargs):
        """Populates the world with entities based on the given counts."""
        # Player Bot
        x, y = self.get_random_empty_coords()
        self.add_entity(PlayerBot(x, y))

        # AI Bots
        for _ in range(kwargs.get('num_gatherer_bots', 0)):
            x, y = self.get_random_empty_coords()
            self.add_entity(GathererBot(x, y))
        for _ in range(kwargs.get('num_repair_bots', 0)):
            x, y = self.get_random_empty_coords()
            self.add_entity(RepairBot(x, y))

        # Enemies
        for _ in range(kwargs.get('num_drones', 0)):
            x, y = self.get_random_empty_coords()
            self.add_entity(MalfunctioningDrone(x, y))
        for _ in range(kwargs.get('num_swarms', 0)):
            x, y = self.get_random_empty_coords()
            self.add_entity(ScavengerSwarm(x, y))

        # Items
        for _ in range(kwargs.get('num_parts', 0)):
            x, y = self.get_random_empty_coords()
            size = random.choice(["small", "medium", "large"])
            self.add_entity(SparePart(x, y, size))
        for _ in range(kwargs.get('num_recharge_stations', 0)):
            x, y = self.get_random_empty_coords()
            self.add_entity(RechargeStation(x, y))

    def find_path(self, start_pos, end_pos):
        """A* pathfinding algorithm. Handles grid wrapping."""
        def heuristic(a, b):
            dx = abs(b[0] - a[0])
            dy = abs(b[1] - a[1])
            return min(dx, self.width - dx) + min(dy, self.height - dy)

        open_set = []
        heapq.heappush(open_set, (0, start_pos))
        came_from = {}
        g_score = {start_pos: 0}
        f_score = {start_pos: heuristic(start_pos, end_pos)}

        while open_set:
            current = heapq.heappop(open_set)[1]
            if current == end_pos:
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]

            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                neighbor = ((current[0] + dx) % self.width, (current[1] + dy) % self.height)
                tentative_g_score = g_score[current] + 1
                if tentative_g_score < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + heuristic(neighbor, end_pos)
                    if neighbor not in [i[1] for i in open_set]:
                        heapq.heappush(open_set, (f_score[neighbor], neighbor))
        return None

    # --- Methods for Statistics ---
    def get_all_bots(self):
        return [e for e in self.entities if isinstance(e, PlayerBot)]
    def increment_parts_collected(self): self._parts_collected_count += 1
    def get_parts_collected_count(self): return self._parts_collected_count
    def get_initial_parts_count(self): return self._initial_parts_count
    def get_bots_destroyed_count(self): return self._bots_destroyed_count