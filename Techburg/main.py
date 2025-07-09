# File: main.py

import random
from grid import Grid
from gui import SimulationGUI
from entities import SparePart, PartSize, RechargeStation
from agents.survivor_bot import PlayerBot, GathererBot, RepairBot
from agents.drone import MalfunctioningDrone
from agents.swarm import ScavengerSwarm
from ai.pathfinding import AStarPathfinder

# --- Configuration Constants ---
GRID_SIZE = (30, 30)
NUM_INITIAL_PARTS = 20
NUM_GATHERER_BOTS = 2
NUM_REPAIR_BOTS = 1
NUM_DRONES = 2
NUM_SWARMS = 2

def setup_simulation():
    """Initializes the grid and all its entities."""
    grid = Grid(size=GRID_SIZE)
    
    # Create RechargeStation objects
    station_positions = [(5, 5), (25, 25), (5, 25), (25, 5)]
    grid.stations = [RechargeStation(pos) for pos in station_positions]

    # Create spare parts
    for _ in range(NUM_INITIAL_PARTS):
        pos = (random.randint(0, grid.width-1), random.randint(0, grid.height-1))
        grid.parts.append(SparePart(pos, random.choice(list(PartSize))))

    # Create the pathfinder with the correct grid size
    pathfinder = AStarPathfinder(GRID_SIZE, obstacles=[])
    
    # Create one player-controlled bot
    player_bot = PlayerBot(bot_id=0, start_pos=(1, 1), pathfinder=pathfinder)
    grid.bots.append(player_bot)

    # Create a mix of AI-controlled Gatherer and Repair bots
    bot_id_counter = 1
    for _ in range(NUM_GATHERER_BOTS):
        pos = (random.randint(0, grid.width-1), random.randint(0, grid.height-1))
        grid.bots.append(GathererBot(bot_id=bot_id_counter, start_pos=pos, pathfinder=pathfinder))
        bot_id_counter += 1
    for _ in range(NUM_REPAIR_BOTS):
        pos = (random.randint(0, grid.width-1), random.randint(0, grid.height-1))
        grid.bots.append(RepairBot(bot_id=bot_id_counter, start_pos=pos, pathfinder=pathfinder))
        bot_id_counter += 1
    
    # Create drones and swarms
    for _ in range(NUM_DRONES):
        pos = (random.randint(0, grid.width-1), random.randint(0, grid.height-1))
        grid.drones.append(MalfunctioningDrone(pos))
    for _ in range(NUM_SWARMS):
        pos = (random.randint(0, grid.width-1), random.randint(0, grid.height-1))
        grid.swarms.append(ScavengerSwarm(pos))

    return grid, player_bot, pathfinder

def handle_bot_replication(grid: Grid, pathfinder: AStarPathfinder):
    """Checks for and handles bot replication at stations, including energy costs."""
    for station in grid.stations:
        bots_at_station = [bot for bot in grid.bots if bot.position == station.position]
        
        parent_repair_bot = next((bot for bot in bots_at_station if isinstance(bot, RepairBot)), None)
        parent_gatherer_bot = next((bot for bot in bots_at_station if isinstance(bot, GathererBot)), None)

        if parent_repair_bot and parent_gatherer_bot:
            if random.random() < 0.20 and parent_repair_bot.energy > 30 and parent_gatherer_bot.energy > 30:
                parent_repair_bot.energy -= 30
                parent_gatherer_bot.energy -= 30
                new_bot_id = max([b.id for b in grid.bots], default=0) + 1
                grid.bots.append(GathererBot(new_bot_id, station.position, pathfinder))
                print(f"*** New Gatherer Bot created at station {station.position}! ***")

            if random.random() < 0.05 and parent_repair_bot.energy > 50 and parent_gatherer_bot.energy > 50:
                parent_repair_bot.energy -= 50
                parent_gatherer_bot.energy -= 50
                new_bot_id = max([b.id for b in grid.bots], default=0) + 1
                grid.bots.append(RepairBot(new_bot_id, station.position, pathfinder))
                print(f"*** New Repair Bot created at station {station.position}! ***")

def main():
    """Main function to initialize and run the turn-based simulation."""
    grid, player_bot, pathfinder = setup_simulation()
    gui = SimulationGUI(grid=grid)

    ai_agents = [bot for bot in grid.bots if not isinstance(bot, PlayerBot)] + grid.drones + grid.swarms

    def handle_player_action():
        station_at_loc = next((s for s in grid.stations if s.position == player_bot.position), None)
        if station_at_loc:
            if player_bot.carried_part:
                station_at_loc.inventory.append(player_bot.carried_part)
                player_bot.carried_part = None
            else:
                player_bot.energy = min(player_bot.energy_capacity, player_bot.energy + 25)
            return
        part_at_loc = next((p for p in grid.parts if p.position == player_bot.position), None)
        if part_at_loc and not player_bot.carried_part:
            player_bot.carried_part = part_at_loc
            grid.parts.remove(part_at_loc)

    def handle_player_upgrade(key: str):
        station_at_loc = next((s for s in grid.stations if s.position == player_bot.position), None)
        if not station_at_loc or not station_at_loc.inventory: return
        part_to_consume = station_at_loc.inventory.pop(0)
        enhancement = part_to_consume.enhancement_value
        if key == "1": player_bot.speed_enhancement += enhancement
        elif key == "2": player_bot.vision_enhancement += enhancement
        elif key == "3": player_bot.energy_capacity += enhancement

    def key_press_handler(event):
        action_taken = True
        if event.keysym in ["Up", "Down", "Left", "Right"]:
            x, y = player_bot.position
            if event.keysym == "Up": y -= 1
            elif event.keysym == "Down": y += 1
            elif event.keysym == "Left": x -= 1
            elif event.keysym == "Right": x += 1
            player_bot.position = grid.wrap_position((x, y))
            player_bot.energy -= 1
        elif event.keysym == "space":
            handle_player_action()
        elif event.keysym in ["1", "2", "3"]:
            handle_player_upgrade(event.keysym)
        else:
            action_taken = False

        if action_taken:
            for agent in ai_agents:
                agent.think(grid)
                agent.move(grid)
            handle_bot_replication(grid, pathfinder)
            for part in grid.parts:
                part.corrode()

        gui.update_display()
        status1 = f"Energy: {player_bot.energy:.0f}/{player_bot.energy_capacity:.0f} | Carrying: {player_bot.carried_part.size.name if player_bot.carried_part else 'Nothing'}"
        status2 = f"Upgrades: Speed {player_bot.speed_enhancement:.0f}% | Vision {player_bot.vision_enhancement:.0f}%"
        gui.update_status(f"{status1} || {status2}")
        
        if not grid.parts or player_bot not in grid.bots:
            gui.update_status("--- SIMULATION OVER ---")
    
    gui.update_display()
    gui.update_status("Arrow Keys: Move | Spacebar: Interact | At Station, 1-2-3: Upgrade")
    gui.bind_keys(key_press_handler)
    gui.start()

if __name__ == "__main__":
    main() 