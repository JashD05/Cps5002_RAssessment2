# Techburg/grid.py
import random
from agents.survivor_bot import PlayerBot, GathererBot, RepairBot, SurvivorBot
from agents.drone import MalfunctioningDrone
from agents.swarm import ScavengerSwarm
from entities import SparePart, RechargeStation

class Grid:
    def __init__(self, width, height, logger_func=None):
        self.width, self.height = width, height
        self.entities, self.parts_collected, self.initial_part_count = [], 0, 0
        self.log = logger_func if logger_func else lambda msg: None

    def is_valid(self, x, y): return 0 <= x < self.width and 0 <= y < self.height
    def get_entity(self, x, y):
        for e in self.entities:
            if e.x == x and e.y == y: return e
        return None
    def add_entity(self, entity): self.entities.append(entity)
    def remove_entity(self, entity):
        if entity in self.entities: self.entities.remove(entity)
    def move_entity(self, entity, new_x, new_y):
        entity.x, entity.y = new_x % self.width, new_y % self.height
    def get_all_bots(self): return [e for e in self.entities if isinstance(e, SurvivorBot)]
    def increment_parts_collected(self): self.parts_collected += 1

    def populate_world(self, num_parts, num_stations, num_drones, num_swarms, num_gatherers, num_repair_bots):
        self.initial_part_count = num_parts
        entities = [PlayerBot('survivor_main', 0, 0)]
        for i in range(num_gatherers): entities.append(GathererBot(f'gatherer_{i}', 0, 0))
        for i in range(num_repair_bots): entities.append(RepairBot(f'repair_{i}', 0, 0))
        for _ in range(num_drones): entities.append(MalfunctioningDrone(0, 0))
        for _ in range(num_swarms): entities.append(ScavengerSwarm(0, 0))
        for _ in range(num_parts): entities.append(SparePart(random.choice(['small','medium','large']), 0, 0))
        for _ in range(num_stations): entities.append(RechargeStation(0, 0))
        for e in entities: self.add_at_empty(e)
        return entities[0]

    def add_at_empty(self, entity):
        while True:
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            if not self.get_entity(x, y):
                entity.x, entity.y = x, y
                self.add_entity(entity)
                break

    def update_world(self):
        for e in self.entities[:]:
            if e in self.entities: e.update(self)
        bots_to_remove = [b for b in self.get_all_bots() if b.energy <= 0]
        for bot in bots_to_remove:
            self.log(f"[EVENT] {bot.bot_id} destroyed!")
            self.remove_entity(bot)