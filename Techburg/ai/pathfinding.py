# File: ai/pathfinding.py

import heapq
from typing import List, Tuple, Optional

class Node:
    def __init__(self, position: Tuple[int, int], parent=None):
        self.position, self.parent = position, parent
        self.g, self.h, self.f = 0, 0, 0
    def __eq__(self, other): return self.position == other.position
    def __lt__(self, other): return self.f < other.f
    def __hash__(self): return hash(self.position)

class AStarPathfinder:
    def __init__(self, grid_size: Tuple[int, int], obstacles: List[Tuple[int, int]]):
        self.grid_width, self.grid_height = grid_size
        self.obstacles = set(obstacles)

    def update_obstacles(self, new_obstacle_positions: List[Tuple[int, int]]):
        self.obstacles = set(new_obstacle_positions)

    def _get_heuristic(self, node_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> int:
        dx, dy = abs(node_pos[0] - end_pos[0]), abs(node_pos[1] - end_pos[1])
        return min(dx, self.grid_width - dx) + min(dy, self.grid_height - dy)

    def find_path(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        start_node, end_node = Node(start_pos), Node(end_pos)
        open_list, closed_set = [], set()
        heapq.heappush(open_list, start_node)

        while open_list:
            current_node = heapq.heappop(open_list)
            if current_node.position in closed_set: continue
            closed_set.add(current_node.position)

            if current_node == end_node:
                path = []
                current = current_node
                while current: path.append(current.position)
                return path[::-1]

            for new_pos in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                node_pos = ((current_node.position[0] + new_pos[0]) % self.grid_width, (current_node.position[1] + new_pos[1]) % self.grid_height)
                if node_pos in self.obstacles: continue
                
                child = Node(node_pos, current_node)
                child.g = current_node.g + 1
                child.h = self._get_heuristic(child.position, end_node.position)
                child.f = child.g + child.h
                heapq.heappush(open_list, child)
        return None