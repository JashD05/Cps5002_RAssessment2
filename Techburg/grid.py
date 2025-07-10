# Techburg/grid.py
import random
from agents.survivor_bot import PlayerBot, GathererBot, RepairBot, SurvivorBot
from agents.drone import MalfunctioningDrone
from agents.swarm import ScavengerSwarm
from entities import SparePart, RechargeStation

class Grid:
    def __init__(self, width, height, logger_func=None):
        self.width = width
        self.height = height
        self.entities = []
        self.parts_collected = 0
        self.initial_part_count = 0
        # A simple logger function that can be passed from the GUI
        self.log = logger_func if logger_func else lambda message: None

    def is_valid(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_entity(self, x, y):
        for entity in self.entities:
            if entity.x == x and entity.y == y: return entity
        return None

    def add_entity(self, entity):
        if self.is_valid(entity.x, entity.y): self.entities.append(entity)

    def remove_entity(self, entity):
        if entity in self.entities: self.entities.remove(entity)

    def move_entity(self, entity, new_x, new_y):
        entity.x = new_x; entity.y = new_y
        
    def get_all_bots(self):
        return [e for e in self.entities if isinstance(e, SurvivorBot)]
    
    def get_threats(self):
        return [e for e in self.entities if isinstance(e, (MalfunctioningDrone, ScavengerSwarm))]

    def increment_parts_collected(self):
        self.parts_collected += 1

    def populate_world(self, num_parts, num_stations, num_drones, num_swarms, num_gatherers, num_repair_bots):
        self.initial_part_count = num_parts
        player_instance = PlayerBot('player', 0, 0)
        entities_to_place = [player_instance]
        for i in range(num_gatherers): entities_to_place.append(GathererBot(f'gatherer_{i}', 0, 0))
        for i in range(num_repair_bots): entities_to_place.append(RepairBot(f'repair_{i}', 0, 0))
        for _ in range(num_drones): entities_to_place.append(MalfunctioningDrone(0, 0))
        for _ in range(num_swarms): entities_to_place.append(ScavengerSwarm(0, 0))
        for _ in range(num_parts): entities_to_place.append(SparePart(random.choice(['small', 'medium', 'large']), 0, 0))
        for _ in range(num_stations): entities_to_place.append(RechargeStation(0, 0))

        for entity in entities_to_place: self.add_at_empty(entity)
        return player_instance

    def add_at_empty(self, entity):
        while True:
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            if not self.get_entity(x, y):
                entity.x, entity.y = x, y
                self.add_entity(entity)
                break

    def update_world(self):
        for entity in self.entities[:]:
            if entity in self.entities: entity.update(self)
        
        bots_to_remove = [e for e in self.get_all_bots() if hasattr(e, 'energy') and e.energy <= 0]
        if bots_to_remove:
            for bot in bots_to_remove:
                self.log(f"[EVENT] {bot.bot_id} has been destroyed!")
                self.remove_entity(bot)