# Techburg/agents/survivor_bot.py
import math, random
from ai.pathfinding import find_path 
from entities import SparePart

class SurvivorBot:
    def __init__(self, bot_id, x, y, energy):
        self.bot_id = bot_id; self.x = x; self.y = y; self.energy = energy
        self.base_max_energy = 200; self.base_speed = 1; self.base_vision = 7
        self.max_energy, self.speed, self.vision = self.base_max_energy, self.base_speed, self.base_vision
        self.energy_depletion_rate = 0.1
        self.carrying_part, self.path = None, []
        self.type = 'survivor_bot'; self.color = "deep sky blue"
        self.stunned, self.active_enhancements = 0, {}
        self.threat_detection_radius = 5
        self.known_parts = set(); self.known_threats = set()

    def update(self, grid):
        if self.energy <= 0: return
        if self.stunned > 0: self.stunned -= 1; grid.log(f"[STATUS] {self.bot_id} is stunned."); return
        self.energy -= self.energy_depletion_rate
        self.update_enhancements(grid); self.update_knowledge(grid)
        self.execute_state_action(grid)

    def execute_state_action(self, grid):
        if not self.path: self.get_new_goal_and_path(grid)
        if self.path:
            next_pos = self.path.pop(0)
            grid.move_entity(self, next_pos[0], next_pos[1])
            if not self.path:
                 entity_at_pos = grid.get_entity(self.x, self.y)
                 if entity_at_pos: self.handle_arrival(entity_at_pos, grid)

    def get_new_goal_and_path(self, grid):
        target, target_pos = None, None
        nearest_threat = self.find_nearest_threat(grid, self.threat_detection_radius)
        if nearest_threat:
            flee_x, flee_y = self.x - (nearest_threat.x - self.x), self.y - (nearest_threat.y - self.y)
            target_pos = (max(0,min(grid.width-1,int(flee_x))), max(0,min(grid.height-1,int(flee_y))))
            if self.carrying_part: self.drop_part(grid)
        if not target_pos:
            if self.energy < self.max_energy * 0.5: target = self.find_nearest_station(grid)
            elif self.carrying_part: target = self.find_nearest_station(grid)
            else: target = self.choose_best_part(grid)
        if target: target_pos = (target.x, target.y)
        if target_pos: self.path = find_path(grid, (self.x, self.y), target_pos)

    def choose_best_part(self, grid):
        """Calculates a score for all known parts and returns the best target."""
        parts = [grid.get_entity(loc[0], loc[1]) for loc in grid.shared_knowledge["parts"]]
        parts = [p for p in parts if p] # Filter out None entries
        if not parts: return None

        best_score = -float('inf')
        best_part = None
        for part in parts:
            dist = len(find_path(grid, (self.x, self.y), (part.x, part.y)) or [])
            if dist == 0: continue
            threat_level = sum(1 for threat_loc in grid.shared_knowledge["threats"] if math.hypot(part.x-threat_loc[0], part.y-threat_loc[1]) < 5)
            score = (part.enhancement_value / dist) - (threat_level * 50) # high penalty for threats
            if score > best_score:
                best_score = score
                best_part = part
        return best_part

    def handle_arrival(self, entity, grid):
        if entity.type == 'recharge_station':
            self.energy = self.max_energy
            if self.carrying_part: grid.increment_parts_collected(); self.carrying_part = None
            self.known_parts.update(grid.shared_knowledge['parts'])
            self.known_threats.update(grid.shared_knowledge['threats'])
        elif entity.type == 'spare_part': self.pickup_part(entity, grid)

    def find_nearest_station(self, grid):
        stations = [e for e in grid.entities if e.type == 'recharge_station']
        available = [s for s in stations if len(grid.get_bots_at_location(s.x, s.y)) < s.max_capacity] if stations else []
        return min(available, key=lambda t:len(find_path(grid,(self.x,self.y),(t.x,t.y)) or [0]*999)) if available else None
        
    def find_nearest_threat(self, grid, radius):
        threats = grid.get_threats()
        nearby = [t for t in threats if math.hypot(self.x-t.x, self.y-t.y) <= radius]
        return min(nearby, key=lambda t: math.hypot(self.x-t.x, self.y-t.y)) if nearby else None

    def update_knowledge(self, grid):
        for entity in grid.entities:
            if math.hypot(self.x-entity.x, self.y-entity.y) <= self.vision:
                if entity.type == 'spare_part': self.known_parts.add((entity.x, entity.y))
                elif entity.type in ['drone', 'swarm']: self.known_threats.add((entity.x, entity.y))

    def pickup_part(self, part, grid):
        if not self.carrying_part and part in grid.entities:
            grid.log(f"[EVENT] {self.bot_id} picked up {part.size} part (Value: {part.enhancement_value:.1f})")
            self.carrying_part = part; grid.remove_entity(part); self.apply_enhancement(part); self.path = []
            
    def drop_part(self, grid):
        if self.carrying_part:
            grid.log(f"[EVENT] {self.bot_id} dropped a part to flee from danger.")
            self.carrying_part.x, self.carrying_part.y = self.x, self.y
            grid.add_entity(self.carrying_part); self.carrying_part = None

    def apply_enhancement(self, part):
        self.active_enhancements[part.enhancement_type] = part.enhancement_value; self.recalculate_stats()

    def update_enhancements(self, grid):
        expired = [e for e, val in self.active_enhancements.items() if val <= 0]
        for e in expired: del self.active_enhancements[e]
        if expired: self.recalculate_stats()
        for e in self.active_enhancements: self.active_enhancements[e] -= 0.1

    def recalculate_stats(self):
        self.max_energy = self.base_max_energy + self.active_enhancements.get('energy_capacity', 0)
        self.speed = self.base_speed * (1 + self.active_enhancements.get('speed', 0) / 200)
        self.vision = self.base_vision + (self.active_enhancements.get('vision', 0) / 20)

class GathererBot(SurvivorBot):
    def __init__(self, bot_id, x, y): super().__init__(bot_id, x, y, energy=200); self.type = 'gatherer_bot'; self.color = "light sea green"
class RepairBot(SurvivorBot):
    def __init__(self, bot_id, x, y): super().__init__(bot_id, x, y, energy=250); self.type = 'repair_bot'; self.color = "cornflower blue"
class PlayerBot(SurvivorBot):
    def __init__(self, bot_id, x, y): super().__init__(bot_id, x, y, energy=300); self.type = 'player_bot'; self.color = "orange"; self.energy_depletion_rate = 0.08
    def update(self, grid):
        if self.energy <= 0: return
        self.energy -= self.energy_depletion_rate; self.update_enhancements(grid)