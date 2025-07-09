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
        """
        The base update method. Most entities will override this.
        By default, an entity does nothing.
        """
        pass

# ==============================================================================
# --- SURVIVOR BOT CLASSES ---
# ==============================================================================

class SurvivorBot(Entity):
    """A base class for all bot types, containing shared logic."""
    def __init__(self, x, y, bot_type, color):
        super().__init__(x, y, bot_type, color)
        self.energy = 100
        self.energy_depletion_rate = 5
        self.carrying_part = None
        self.path = [] # The current path the bot is following

    def update(self, grid):
        """Defines the bot's decision-making process each turn."""
        # If the bot has a path, it follows it.
        if self.path:
            next_pos = self.path.pop(0)
            # Basic energy check before moving
            if self.energy > self.energy_depletion_rate:
                grid.move_entity(self, next_pos[0], next_pos[1])
                self.energy -= self.energy_depletion_rate
            else:
                self.energy = 0 # Bot runs out of energy
                print(f"{self.type} at ({self.x}, {self.y}) ran out of energy.")
            return

        # AI Decision Making: What should I do now?
        # 1. If carrying a part, find the nearest recharge station.
        if self.carrying_part:
            station = self.find_nearest(grid, 'recharge_station')
            if station:
                self.path = grid.find_path((self.x, self.y), (station.x, station.y))
                # Drop the first step because it's the current location
                if self.path: self.path.pop(0)
        # 2. If not carrying a part, find the nearest part to pick up.
        else:
            part = self.find_nearest(grid, 'part')
            if part:
                self.path = grid.find_path((self.x, self.y), (part.x, part.y))
                if self.path: self.path.pop(0)

        # Interaction logic: pick up or drop off parts
        entity_at_pos = grid.get_entity(self.x, self.y)
        if entity_at_pos:
            if "part" in entity_at_pos.type and not self.carrying_part:
                self.pickup_part(entity_at_pos, grid)
            elif entity_at_pos.type == 'recharge_station' and self.carrying_part:
                self.dropoff_part(grid)

    def find_nearest(self, grid, entity_type_prefix):
        """Finds the closest entity of a given type."""
        targets = [e for e in grid.entities if e.type.startswith(entity_type_prefix)]
        if not targets:
            return None

        # Calculate distance to all targets and find the minimum
        closest_target = min(
            targets,
            key=lambda t: math.hypot(self.x - t.x, self.y - t.y)
        )
        return closest_target

    def pickup_part(self, part, grid):
        """Picks up a spare part from the grid."""
        self.carrying_part = part
        grid.remove_entity(part)
        print(f"{self.type} picked up a {part.size} part.")

    def dropoff_part(self, grid):
        """Drops off a part at a recharge station."""
        print(f"{self.type} dropped off a {self.carrying_part.size} part.")
        grid.increment_parts_collected()
        self.carrying_part = None
        # Bot gains energy for dropping off part
        self.energy = min(100, self.energy + 25)

class PlayerBot(SurvivorBot):
    """The bot controlled by the player. Its logic will be tied to keyboard input."""
    def __init__(self, x, y):
        super().__init__(x, y, "player_bot", "orange")

    # The PlayerBot's update method will likely be handled separately in the
    # main loop based on keyboard events, so it can be left empty here.
    def update(self, grid):
        pass # Player movement is not autonomous

class GathererBot(SurvivorBot):
    """A bot that specializes in collecting parts."""
    def __init__(self, x, y):
        super().__init__(x, y, "gatherer_bot", "light sea green")
        # Gatherers are slightly more energy efficient
        self.energy_depletion_rate = 4

class RepairBot(SurvivorBot):
    """A bot that can create new bots with Gatherers."""
    def __init__(self, x, y):
        super().__init__(x, y, "repair_bot", "cornflower blue")

    # RepairBot could have additional logic for collaboration
    # This would be implemented in its update method.


# ==============================================================================
# --- ENEMY CLASSES ---
# ==============================================================================

class MalfunctioningDrone(Entity):
    """An enemy that pursues and attacks bots."""
    def __init__(self, x, y):
        super().__init__(x, y, "drone", "red")
        self.pursuit_target = None
        self.path = []

    def update(self, grid):
        # If the drone has a path, follow it
        if self.path:
            next_pos = self.path.pop(0)
            grid.move_entity(self, next_pos[0], next_pos[1])
            return

        # Check for nearby bots to pursue
        nearby_bots = self.find_bots_in_range(grid)
        if nearby_bots:
            # Simple logic: target the closest bot
            self.pursuit_target = min(
                nearby_bots,
                key=lambda b: math.hypot(self.x - b.x, self.y - b.y)
            )
            # Find a path to the target
            self.path = grid.find_path((self.x, self.y), (self.pursuit_target.x, self.pursuit_target.y))
            if self.path: self.path.pop(0)
        else:
            # If no bots are nearby, move randomly
            self.move_randomly(grid)

    def find_bots_in_range(self, grid):
        """Finds bots within the drone's vision range."""
        bots_in_range = []
        for entity in grid.get_all_bots():
            distance = math.hypot(self.x - entity.x, self.y - entity.y)
            if distance <= VISION_RANGE:
                bots_in_range.append(entity)
        return bots_in_range

    def move_randomly(self, grid):
        """Moves the drone to a random adjacent cell."""
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x = (self.x + dx) % grid.width
        new_y = (self.y + dy) % grid.height
        grid.move_entity(self, new_x, new_y)


class ScavengerSwarm(Entity):
    """An enemy that consumes parts and moves randomly."""
    def __init__(self, x, y):
        super().__init__(x, y, "swarm", "lawn green")

    def update(self, grid):
        # Check if standing on a part
        entity_at_pos = grid.get_entity(self.x, self.y)
        if entity_at_pos and "part" in entity_at_pos.type:
            print(f"Swarm consumed a {entity_at_pos.size} part.")
            grid.remove_entity(entity_at_pos)
        else:
            # Move to a random adjacent cell
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            new_x = (self.x + dx) % grid.width
            new_y = (self.y + dy) % grid.height
            grid.move_entity(self, new_x, new_y)


# ==============================================================================
# --- ITEM CLASSES ---
# ==============================================================================

class SparePart(Entity):
    """A part that can be collected by bots."""
    def __init__(self, x, y, size="small"):
        self.size = size
        color_map = {"small": "cyan", "medium": "magenta", "large": "yellow"}
        super().__init__(x, y, f"{size}_part", color_map.get(size))
        # Set value based on size
        value_map = {"small": 3.0, "medium": 5.0, "large": 7.0}
        self.value = value_map.get(size)

    def update(self, grid):
        """Parts corrode over time, losing value."""
        self.corrode()

    def corrode(self):
        """Reduces the part's value slightly each turn."""
        self.value = max(0, self.value - 0.001)


class RechargeStation(Entity):
    """A fixed location for bots to recharge and drop off parts."""
    def __init__(self, x, y):
        super().__init__(x, y, "recharge_station", "purple")

    # Recharge stations are static and don't need an update method.