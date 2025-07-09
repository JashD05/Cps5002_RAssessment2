# File: entities.py
import random
import math

# A constant to define how far drones and bots can "see"
VISION_RANGE = 3

class Entity:
    """A base class for all objects in the simulation."""
    def __init__(self, x, y, entity_type, color):
        self.x = x
        self.y = y
        self.type = entity_type
        self.color = color

    def update(self, grid):
        """The base update method. Most entities will override this."""
        pass

# ==============================================================================
# --- SURVIVOR BOT CLASSES ---
# ==============================================================================

class SurvivorBot(Entity):
    """A base class for all bot types, containing shared AI logic."""
    def __init__(self, x, y, bot_type, color):
        super().__init__(x, y, bot_type, color)
        self.energy = 100
        self.energy_depletion_rate = 5
        self.carrying_part = None
        self.path = [] # The current path the bot is following

    def update(self, grid):
        """Defines the bot's AI decision-making process each turn."""
        # --- Interaction Logic ---
        # First, check if we are on a square we can interact with.
        entity_at_pos = grid.get_entity(self.x, self.y)
        if entity_at_pos:
            # If we are on a part and not carrying anything, pick it up.
            if "part" in entity_at_pos.type and not self.carrying_part:
                self.pickup_part(entity_at_pos, grid)
                self.path = [] # Clear path after picking up, to force re-evaluation.
                return # End turn here
            # If we are at a station and carrying a part, drop it off.
            elif entity_at_pos.type == 'recharge_station' and self.carrying_part:
                self.dropoff_part(grid)
                self.path = [] # Clear path after dropping off.
                return # End turn here

        # --- Pathfinding and Goal Selection Logic ---
        # If the bot has a path, it follows it.
        if self.path:
            next_pos = self.path.pop(0)
            if self.energy > self.energy_depletion_rate:
                grid.move_entity(self, next_pos[0], next_pos[1])
                self.energy -= self.energy_depletion_rate
            else:
                self.energy = 0
                print(f"{self.type} at ({self.x}, {self.y}) ran out of energy.")
            return

        # --- If idle (no path), decide on a new goal ---
        # 1. If carrying a part, find the nearest recharge station.
        if self.carrying_part:
            station = self.find_nearest(grid, 'recharge_station')
            if station:
                new_path = grid.find_path((self.x, self.y), (station.x, station.y))
                if new_path: self.path = new_path[1:] # Discard first step
        # 2. If not carrying a part, find the nearest part.
        else:
            part = self.find_nearest(grid, '_part') # Use underscore to match all part types
            if part:
                new_path = grid.find_path((self.x, self.y), (part.x, part.y))
                if new_path: self.path = new_path[1:] # Discard first step

    def find_nearest(self, grid, entity_type_suffix):
        """Finds the closest entity of a given type."""
        targets = [e for e in grid.entities if e.type.endswith(entity_type_suffix)]
        if not targets: return None
        return min(targets, key=lambda t: math.hypot(self.x - t.x, self.y - t.y))

    def pickup_part(self, part, grid):
        self.carrying_part = part
        grid.remove_entity(part)
        print(f"{self.type} picked up a {part.size} part.")

    def dropoff_part(self, grid):
        print(f"{self.type} dropped off a {self.carrying_part.size} part.")
        grid.increment_parts_collected()
        self.carrying_part = None
        self.energy = min(100, self.energy + 25)

class PlayerBot(SurvivorBot):
    """The bot controlled by the player."""
    def __init__(self, x, y):
        super().__init__(x, y, "player_bot", "orange")
    def update(self, grid):
        # Player movement is not autonomous.
        pass

class GathererBot(SurvivorBot):
    """A bot that specializes in collecting parts."""
    def __init__(self, x, y):
        super().__init__(x, y, "gatherer_bot", "light sea green")
        self.energy_depletion_rate = 4

class RepairBot(SurvivorBot):
    """A bot that can create new bots with Gatherers."""
    def __init__(self, x, y):
        super().__init__(x, y, "repair_bot", "cornflower blue")

# ==============================================================================
# --- ENEMY CLASSES (with AI) ---
# ==============================================================================
class MalfunctioningDrone(Entity):
    """An enemy that pursues and attacks bots."""
    def __init__(self, x, y):
        super().__init__(x, y, "drone", "red")
        self.path = []

    def update(self, grid):
        if self.path:
            next_pos = self.path.pop(0)
            grid.move_entity(self, next_pos[0], next_pos[1])
            return

        nearby_bots = [b for b in grid.get_all_bots() if math.hypot(self.x - b.x, self.y - b.y) <= VISION_RANGE]
        if nearby_bots:
            target = min(nearby_bots, key=lambda b: math.hypot(self.x - b.x, self.y - b.y))
            new_path = grid.find_path((self.x, self.y), (target.x, target.y))
            if new_path: self.path = new_path[1:]
        else:
            self.move_randomly(grid)

    def move_randomly(self, grid):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        grid.move_entity(self, (self.x + dx) % grid.width, (self.y + dy) % grid.height)

class ScavengerSwarm(Entity):
    """An enemy that consumes parts and moves randomly."""
    def __init__(self, x, y):
        super().__init__(x, y, "swarm", "lawn green")

    def update(self, grid):
        entity_at_pos = grid.get_entity(self.x, self.y)
        if entity_at_pos and "part" in entity_at_pos.type:
            print(f"Swarm consumed a {entity_at_pos.size} part.")
            grid.remove_entity(entity_at_pos)
        else:
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            grid.move_entity(self, (self.x + dx) % grid.width, (self.y + dy) % grid.height)

# ==============================================================================
# --- ITEM CLASSES ---
# ==============================================================================
class SparePart(Entity):
    """A part that can be collected by bots."""
    def __init__(self, x, y, size="small"):
        self.size = size
        color_map = {"small": "cyan", "medium": "magenta", "large": "yellow"}
        super().__init__(x, y, f"{size}_part", color_map.get(size))
        value_map = {"small": 3.0, "medium": 5.0, "large": 7.0}
        self.value = value_map.get(size)

    def update(self, grid):
        self.value = max(0, self.value - 0.001)

class RechargeStation(Entity):
    """A fixed location for bots to recharge and drop off parts."""
    def __init__(self, x, y):
        super().__init__(x, y, "recharge_station", "purple")