# File: ai/pathfinding.py

import heapq
from typing import List, Tuple, Optional

class Node:
    """A node in the A* search graph, representing a cell in the grid."""
    def __init__(self, position: Tuple[int, int], parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

    def __hash__(self):
        return hash(self.position)

class AStarPathfinder:
    """Implements the A* pathfinding algorithm for a toroidal grid."""
    def __init__(self, grid_size: Tuple[int, int], obstacles: List[Tuple[int, int]]):
        self.grid_width, self.grid_height = grid_size
        self.obstacles = set(obstacles)

    def update_obstacles(self, new_obstacle_positions: List[Tuple[int, int]]):
        """Allows for updating the obstacle list for a dynamic environment."""
        self.obstacles = set(new_obstacle_positions)

    def _get_heuristic(self, node_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> int:
        """Calculate Manhattan distance on a wrap-around grid."""
        dx = abs(node_pos[0] - end_pos[0])
        dy = abs(node_pos[1] - end_pos[1])
        wrapped_dx = min(dx, self.grid_width - dx)
        wrapped_dy = min(dy, self.grid_height - dy)
        return wrapped_dx + wrapped_dy

    def find_path(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]) -> Optional[List[Tuple[int, int]]]:
        start_node = Node(start_pos)
        end_node = Node(end_pos)
        open_list = []
        closed_set = set()
        heapq.heappush(open_list, start_node)

        while open_list:
            current_node = heapq.heappop(open_list)
            closed_set.add(current_node.position)

            if current_node == end_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                return path[::-1]

            children = []
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                node_position = (
                    (current_node.position[0] + new_position[0]) % self.grid_width,
                    (current_node.position[1] + new_position[1]) % self.grid_height
                )
                if node_position in self.obstacles or node_position in closed_set:
                    continue
                new_node = Node(node_position, current_node)
                children.append(new_node)

            for child in children:
                child.g = current_node.g + 1
                child.h = self._get_heuristic(child.position, end_node.position)
                child.f = child.g + child.h
                if any(open_node for open_node in open_list if child == open_node and child.g > open_node.g):
                    continue
                heapq.heappush(open_list, child)
        return None