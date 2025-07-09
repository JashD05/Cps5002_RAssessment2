# File: Techburg/ai/pathfinding.py
import heapq

def find_path(grid, start, end):
    """
    Finds the shortest path between two points on the grid using the A* algorithm.
    Correctly handles the grid wrapping around the edges (toroidal).

    Args:
        grid: The main grid object, used to get world dimensions.
        start: A tuple (x, y) for the starting position.
        end: A tuple (x, y) for the target position.

    Returns:
        A list of (x, y) tuples representing the path from start to end,
        or None if no path is found.
    """
    
    def heuristic(a, b):
        """Calculates the toroidal distance heuristic for A*."""
        dx = abs(b[0] - a[0])
        dy = abs(b[1] - a[1])
        # Consider the wrap-around distance for both axes
        shortest_dx = min(dx, grid.width - dx)
        shortest_dy = min(dy, grid.height - dy)
        return shortest_dx + shortest_dy

    open_set = []
    heapq.heappush(open_set, (0, start))  # (f_score, node)

    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, end)}

    while open_set:
        current = heapq.heappop(open_set)[1]

        if current == end:
            # Reconstruct the path from end to start
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]  # Return the reversed path

        # Explore neighbors
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = ((current[0] + dx) % grid.width, (current[1] + dy) % grid.height)

            # Cost of moving to a neighbor is always 1
            tentative_g_score = g_score[current] + 1

            if tentative_g_score < g_score.get(neighbor, float('inf')):
                # This path to neighbor is better than any previous one. Record it.
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, end)
                
                # Check if neighbor is in open_set to avoid duplicates
                if neighbor not in [i[1] for i in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    return None  # No path found