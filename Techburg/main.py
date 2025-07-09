# File: main.py

import random
from grid import Grid
from gui import SimulationGUI
from entities import SparePart, PartSize
from agents.survivor_bot import SurvivorBot
from agents.drone import MalfunctioningDrone
from agents.swarm import ScavengerSwarm
from ai.pathfinding import AStarPathfinder

# --- Configuration Constants ---
GRID_SIZE = (30, 30)
NUM_INITIAL_PARTS = 20
NUM_BOTS = 3
NUM_DRONES = 2
NUM_SWARMS = 2
SIMULATION_SPEED_MS = 100 # A faster speed is now possible

def setup_simulation():
    """Initializes the grid and all its entities."""
    grid = Grid(size=GRID_SIZE)
    grid.stations = [(5, 5), (25, 25), (5, 25), (25, 5)]

    for _ in range(NUM_INITIAL_PARTS):
        pos = (random.randint(0, grid.width-1), random.randint(0, grid.height-1))
        grid.parts.append(SparePart(pos, random.choice(list(PartSize))))

    pathfinder = AStarPathfinder(GRID_SIZE, obstacles=[])

    for _ in range(NUM_DRONES):
        pos = (random.randint(0, grid.width-1), random.randint(0, grid.height-1))
        grid.drones.append(MalfunctioningDrone(pos))
    for _ in range(NUM_SWARMS):
        pos = (random.randint(0, grid.width-1), random.randint(0, grid.height-1))
        grid.swarms.append(ScavengerSwarm(pos))

    for i in range(NUM_BOTS):
        pos = (random.randint(0, grid.width-1), random.randint(0, grid.height-1))
        bot = SurvivorBot(bot_id=i+1, start_pos=pos, pathfinder=pathfinder)
        grid.bots.append(bot)

    return grid

def update_simulation(grid: Grid, gui: SimulationGUI, agents_to_update: list, current_agent_index: int):
    """Performs one step of the simulation and schedules the next."""
    
    # 1. Have only ONE agent "think" this frame to keep the GUI responsive
    if agents_to_update:
        agent_to_think = agents_to_update[current_agent_index]
        agent_to_think.think(grid)
        current_agent_index = (current_agent_index + 1) % len(agents_to_update)

    # 2. Have ALL agents perform their fast "move" action every frame
    for agent in agents_to_update:
        agent.move(grid)

    # 3. Update World State
    for part in grid.parts:
        part.corrode()

    # 4. Update GUI
    gui.update_display()

    # 5. Check End Conditions and Schedule Next Update
    if grid.parts and grid.bots:
        gui.window.after(SIMULATION_SPEED_MS, lambda: update_simulation(grid, gui, agents_to_update, current_agent_index))
    else:
        print("--- SIMULATION OVER ---")
        gui.window.quit()

def main():
    """Main function to initialize and run the simulation loop."""
    print("--- Setting up Techburg Simulation ---")
    grid = setup_simulation()
    print(f"Setup complete: {len(grid.bots)} bots, {len(grid.drones)} drones, {len(grid.swarms)} swarms, {len(grid.parts)} parts.")
    
    gui = SimulationGUI(grid=grid)

    all_agents = grid.bots + grid.drones + grid.swarms
    
    # Draw the initial state and schedule the simulation to start
    gui.update_display()
    gui.window.after(100, lambda: update_simulation(grid, gui, all_agents, 0))
    gui.start()

if __name__ == "__main__":
    main()