# Techburg/grid.py
import random
from agents.survivor_bot import PlayerBot, GathererBot, RepairBot, SurvivorBot
from agents.drone import MalfunctioningDrone
from agents.swarm import ScavengerSwarm
from entities import SparePart, RechargeStation

class Grid:
    """Manages the simulation world, entities, and their interactions."""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # --- DEBUG LINE ---
        print(f"[DEBUG] Grid Created: width={self.width}, height={self.height}")
        self.entities = []
        self.parts_collected = 0

    def is_valid(self, x, y):
        """Checks if a given coordinate is within the grid boundaries."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_entity(self, x, y):
        """Gets the entity at a specific coordinate."""
        for entity in self.entities:
            if entity.x == x and entity.y == y:
                return entity
        return None

    def add_entity(self, entity):
        """Adds an entity to the grid."""
        if self.is_valid(entity.x, entity.y):
            self.entities.append(entity)

    def remove_entity(self, entity):
        """Removes an entity from the grid."""
        if entity in self.entities:
            self.entities.remove(entity)

    def move_entity(self, entity, new_x, new_y):
        """Moves an entity to a new position."""
        entity.x = new_x
        entity.y = new_y
        
    def get_all_bots(self):
        """Returns a list of all bot objects."""
        bot_types = ['player_bot', 'gatherer_bot', 'repair_bot', 'survivor_bot']
        return [e for e in self.entities if hasattr(e, 'type') and e.type in bot_types]

    def increment_parts_collected(self):
        """Increments the counter for collected parts."""
        self.parts_collected += 1

    def populate_world(self, num_parts, num_stations, num_drones, num_swarms, num_gatherers, num_repair_bots):
        """Populates the grid and returns the player_bot instance."""
        entities_to_place = []
        player_instance = PlayerBot('player', 0, 0)
        entities_to_place.append(player_instance)
        
        for i in range(num_gatherers):
            entities_to_place.append(GathererBot(f'gatherer_{i}', 0, 0))
        for i in range(num_repair_bots):
            entities_to_place.append(RepairBot(f'repair_{i}', 0, 0))
        for _ in range(num_drones):
            entities_to_place.append(MalfunctioningDrone(0, 0))
        for _ in range(num_swarms):
            entities_to_place.append(ScavengerSwarm(0, 0))
        for _ in range(num_parts):
            entities_to_place.append(SparePart(random.choice(['small', 'medium', 'large']), 0, 0))
        for _ in range(num_stations):
            entities_to_place.append(RechargeStation(0, 0))

        for entity in entities_to_place:
            self.add_at_empty(entity)
            
        return player_instance

    def add_at_empty(self, entity):
        """Adds an entity to a random empty cell."""
        # --- DEBUG LINE ---
        if self.height <= 0:
            print(f"[DEBUG] ERROR: Grid height is {self.height}. Cannot generate random y-coordinate.")
            # Set a default y to prevent a crash
            y = 0
        else:
            y = random.randint(0, self.height - 1)

        x = random.randint(0, self.width - 1)
        
        # --- DEBUG LINE ---
        print(f"[DEBUG] Attempting to place {entity.type} at ({x}, {y})")
        
        if not self.get_entity(x, y):
            entity.x = x
            entity.y = y
            self.add_entity(entity)
        else:
            # If the spot is taken, try again (simple retry logic)
            self.add_at_empty(entity)

    def update_world(self):
        """Updates all entities and removes those with no energy."""
        for entity in self.entities[:]:
            if entity in self.entities:
                entity.update(self)
        
        bots_to_remove = [
            e for e in self.get_all_bots() if hasattr(e, 'energy') and e.energy <= 0
        ]
        for bot in bots_to_remove:
            self.remove_entity(bot)