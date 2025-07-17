# Techburg/ai/pathfinding.py
import heapq

def find_path(grid, start, end):
    class Node:
        def __init__(self, parent=None, position=None):
            self.parent, self.position = parent, position; self.g, self.h, self.f = 0, 0, 0
        def __eq__(self, other): return self.position == other.position
        def __lt__(self, other): return self.f < other.f
        def __hash__(self): return hash(self.position)
    start_node, end_node = Node(None, start), Node(None, end)
    open_list, closed_set = [], set()
    heapq.heappush(open_list, (start_node.f, start_node))
    while open_list:
        current_node = heapq.heappop(open_list)[1]
        if current_node.position in closed_set: continue
        closed_set.add(current_node.position)
        if current_node == end_node:
            path = []; current = current_node
            while current is not None: path.append(current.position); current = current.parent
            return path[::-1]
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
            if not grid.is_valid(node_position[0], node_position[1]): continue
            entity = grid.get_entity(node_position[0], node_position[1])
            if entity and entity.type not in ['spare_part', 'recharge_station']: continue
            child = Node(current_node, node_position)
            child.g = current_node.g + 1
            child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])
            child.f = child.g + child.h
            heapq.heappush(open_list, (child.f, child))
    return None