# Techburg/ai/pathfinding.py
import heapq

def find_path(grid, start, end):
    class Node:
        def __init__(self, parent=None, position=None):
            self.parent, self.position = parent, position; self.g, self.h, self.f = 0, 0, 0
        def __eq__(self, other): return self.position == other.position
        def __lt__(self, other): return self.f < other.f
    start_node, end_node = Node(None, start), Node(None, end)
    open_list, closed_list = [], set()
    heapq.heappush(open_list, (start_node.f, start_node))
    while len(open_list) > 0:
        current_node = heapq.heappop(open_list)[1]
        closed_list.add(current_node.position)
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None: path.append(current.position); current = current.parent
            return path[::-1]
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1,-1), (-1,1), (1,-1), (1,1)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])
            if not grid.is_valid(node_position[0], node_position[1]): continue
            entity_at_pos = grid.get_entity(node_position[0], node_position[1])
            if entity_at_pos and entity_at_pos.type not in ['spare_part', 'recharge_station']: continue
            children.append(Node(current_node, node_position))
        for child in children:
            if child.position in closed_list: continue
            child.g, child.h = current_node.g + 1, ((child.position[0]-end_node.position[0])**2) + ((child.position[1]-end_node.position[1])**2)
            child.f = child.g + child.h
            if any(o for f, o in open_list if child == o and child.g > o.g): continue
            heapq.heappush(open_list, (child.f, child))
    return None