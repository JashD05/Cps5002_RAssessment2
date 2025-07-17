# Techburg/ai/pathfinding.py
import heapq

def find_path(grid, start, end):
    """
    A robust A* pathfinding algorithm to prevent crashes.
    """
    class Node:
        """A node class for A* Pathfinding"""
        def __init__(self, parent=None, position=None):
            self.parent = parent
            self.position = position
            self.g = 0  # Cost from start to current Node
            self.h = 0  # Heuristic cost from current Node to end
            self.f = 0  # Total cost (g + h)
        
        # Define how nodes are compared, which is essential for the heap
        def __lt__(self, other):
          return self.f < other.f
        
        # Define how to check for equality
        def __eq__(self, other):
            return self.position == other.position
        
        # Define how to hash a node, which is essential for using it in sets
        def __hash__(self):
            return hash(self.position)

    # Create start and end nodes
    start_node = Node(None, start)
    end_node = Node(None, end)

    # Initialize both open and closed lists
    open_list = []
    closed_list = set()

    # Heapq is a priority queue, perfect for A*
    heapq.heappush(open_list, (start_node.f, start_node))

    # Loop until you find the end
    while len(open_list) > 0:
        # Get the current node
        current_node = heapq.heappop(open_list)[1]
        closed_list.add(current_node.position)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node
            while current is not None:
                path.append(current.position)
                current = current.parent
            return path[::-1]  # Return reversed path

        # Generate children (adjacent squares)
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure it's within the grid
            if not grid.is_valid(node_position[0], node_position[1]):
                continue
                
            # Make sure it's not on a blocked square (like another bot or threat)
            entity = grid.get_entity(node_position[0], node_position[1])
            if entity and entity.type not in ['spare_part', 'recharge_station']:
                continue

            # If the successor is already on the closed list, skip it
            if node_position in closed_list:
                continue

            # Create new node
            child = Node(current_node, node_position)

            # Calculate costs
            child.g = current_node.g + 1
            # Heuristic: Manhattan distance
            child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1])
            child.f = child.g + child.h

            # If child is already in the open list with a lower 'f' cost, skip
            if any(open_node for f, open_node in open_list if child == open_node and child.g >= open_node.g):
                continue
                
            # Add the child to the open list
            heapq.heappush(open_list, (child.f, child))
            
    return None # Return None if no path is found