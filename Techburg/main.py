# File: main.py

import random
import time
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
SIMULATION_SPEED_SECONDS = 0.2

def setup_simulation():
    """Initializes all components of the Techburg simulation."""
    print("--- Setting up Techburg Simulation ---")
    
    bots, drones, swarms, parts = [], [], [], []
    stations = [(5, 5), (25, 25), (5, 25), (25, 5)]

    for _ in range(NUM_INITIAL_PARTS):
        pos = (random.randint(0, GRID_SIZE[0]-1), random.randint(0, GRID_SIZE[1]-1))
        parts.append(SparePart(pos, random.choice(list(PartSize))))

    # 1. Create the pathfinder first (with no obstacles initially).
    pathfinder = AStarPathfinder(GRID_SIZE, obstacles=[])

    # 2. Create drones and swarms.
    for _ in range(NUM_DRONES):
        pos = (random.randint(0, GRID_SIZE[0]-1), random.randint(0, GRID_SIZE[1]-1))
        drones.append(MalfunctioningDrone(pos))
    for _ in range(NUM_SWARMS):
        pos = (random.randint(0, GRID_SIZE[0]-1), random.randint(0, GRID_SIZE[1]-1))
        swarms.append(ScavengerSwarm(pos))

    # 3. Create survivor bots, injecting the pathfinder.
    for i in range(NUM_BOTS):
        pos = (random.randint(0, GRID_SIZE[0]-1), random.randint(0, GRID_SIZE[1]-1))
        bot = SurvivorBot(bot_id=i+1, start_pos=pos, pathfinder=pathfinder)
        bots.append(bot)

    print(f"Setup complete: {len(bots)} bots, {len(drones)} drones, {len(swarms)} swarms, {len(parts)} parts.")
    return bots, drones, swarms, parts, stations, pathfinder


def main():
    """Main function to initialize and run the simulation loop."""
    gui = SimulationGUI(grid_size=GRID_SIZE)
    bots, drones, swarms, parts, stations, pathfinder = setup_simulation()

    simulation_running = True
    while simulation_running:
        all_entities_for_drawing = bots + drones + swarms + parts
        drawable_stations = [type('obj', (object,), {'position': s, 'color': 'purple'}) for s in stations]
        
        # Agent Actions
        all_threats = drones + swarms
        for bot in bots:
            bot.act(parts, stations, all_threats)
        for drone in drones:
            drone.act(bots)
        for swarm in swarms:
            swarm.act(bots + drones + parts, parts)

        # Update World State
        for part in parts:
            part.corrode()  # [cite: 38]

        # Update GUI
        gui.update_display(all_entities_for_drawing + drawable_stations)

        # [cite_start]Check End Conditions [cite: 94]
        if not parts or not bots:
            simulation_running = False
            print("--- SIMULATION OVER ---")

        time.sleep(SIMULATION_SPEED_SECONDS)

if __name__ == "__main__":
    main()