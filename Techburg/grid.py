# File: Techburg/grid.py
import random
import heapq
from entities import SparePart, RechargeStation
from agents.survivor_bot import PlayerBot, GathererBot, RepairBot, SurvivorBot
from agents.drone import MalfunctioningDrone
from agents.swarm import ScavengerSwarm

class Grid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = {}
        self.entities = []
        self._initial_parts_count = 0
        self._parts_collected_count = 0
        self._bots_destroyed_count = 0

    def add_entity(self, entity):
        self.grid[(entity.x, entity.y)] = entity
        self.entities.append(entity)
        if entity.type == "spare_part":
            self._initial_parts_count += 1

    def move_entity(self, entity, new_x, new_y):
        # To prevent collision, check if the target cell is occupied
        # by anything other than the entity that is moving.
        target_cell_occupant = self.grid.get((new_x, new_y))
        if target_cell_occupant is None:
            if (entity.x, entity.y) in self.grid:
                del self.grid[(entity.x, entity.y)]
            self.grid[(new_x, new_y)] = entity
            entity.x = new_x
            entity.y = new_y
            return True
        return False

    def remove_entity(self, entity):
        if (entity.x, entity.y) in self.grid and self.grid.get((entity.x, entity.y)) == entity:
            del self.grid[(entity.x, entity.y)]
        if entity in self.entities:
            self.entities.remove(entity)

    def get_entity(self, x, y):
        return self.grid.get((x, y))

    def get_random_empty_coords(self):
        while True:
            x, y = random.randint(0, self.width - 1), random.randint(0, self.height - 1)
            if (x, y) not in self.grid:
                return x, y

    def update_world(self):
        """Updates all entities in the world for one simulation step."""
        # Bot death logic
        dead_bots = [e for e in self.get_all_bots() if e.energy <= 0]
        for bot in dead_bots:
            self.remove_entity(bot)
            self._bots_destroyed_count += 1
            print(f"A {bot.type} has been destroyed!")

        # CORRECTED: Loop through all entities, including the player,
        # so their AI logic can run.
        for entity in list(self.entities):
            if entity in self.entities: # Check if the entity wasn't just destroyed
                entity.update(self)

    def check_game_over(self):
        if self._initial_parts_count > 0 and self._parts_collected_count >= self._initial_parts_count:
            return "win"
        if self._initial_parts_count > 0 and not self.get_all_bots():
            return "lose"
        return None

    def populate_world(self, **kwargs):
        x, y = self.get_random_empty_coords(); self.add_entity(PlayerBot(0,x,y))
        for i in range(kwargs.get('num_gatherer_bots', 0)): x, y = self.get_random_empty_coords(); self.add_entity(GathererBot(i+1, x, y))
        for i in range(kwargs.get('num_repair_bots', 0)): x, y = self.get_random_empty_coords(); self.add_entity(RepairBot(100+i, x, y))
        for i in range(kwargs.get('num_drones', 0)): x, y = self.get_random_empty_coords(); self.add_entity(MalfunctioningDrone(x, y))
        for i in range(kwargs.get('num_swarms', 0)): x, y = self.get_random_empty_coords(); self.add_entity(ScavengerSwarm(x, y))
        for i in range(kwargs.get('num_parts', 0)): x, y = self.get_random_empty_coords(); self.add_entity(SparePart(size=random.choice(["small", "medium", "large"]), x=x, y=y))
        for i in range(kwargs.get('num_recharge_stations', 0)): x, y = self.get_random_empty_coords(); self.add_entity(RechargeStation(x, y))

    def get_all_entities_of_type(self, type_prefix):
        return [e for e in self.entities if e.type.startswith(type_prefix)]

    def get_all_bots(self): return [e for e in self.entities if isinstance(e, SurvivorBot)]
    def increment_parts_collected(self): self._parts_collected_count += 1
    def get_parts_collected_count(self): return self._parts_collected_count
    def get_initial_parts_count(self): return self._initial_parts_count
    def get_bots_destroyed_count(self): return self._bots_destroyed_count