# File: Techburg/main.py
import tkinter as tk
from grid import Grid
from gui import SimulationGUI
from agents.survivor_bot import PlayerBot

def main():
    """Main function to initialize and run the Techburg simulation."""
    root = tk.Tk()
    root.title("Techburg Simulation - HARD MODE")

    # --- Game State Variables ---
    game_speed = {'normal': 150, 'fast': 50} # Game is slightly faster overall
    current_speed = 'normal'
    is_game_over = False

    grid = Grid(width=30, height=30)
    gui = SimulationGUI(root, grid)

    # --- HARD MODE SETTINGS ---
    # More enemies, fewer parts and stations.
    grid.populate_world(
        num_gatherer_bots=4,    # Less help
        num_repair_bots=2,
        num_drones=10,          # Way more drones
        num_swarms=8,           # Way more swarms
        num_parts=50,           # Fewer parts to find
        num_recharge_stations=3 # Scarce safe zones
    )
    # --- END HARD MODE ---

    player_bot = [bot for bot in grid.get_all_bots() if isinstance(bot, PlayerBot)][0]

    # --- Key Binding Functions ---
    def set_normal_speed(event=None):
        nonlocal current_speed
        current_speed = 'normal'
        gui.update_speed_display("x1")

    def set_fast_speed(event=None):
        nonlocal current_speed
        current_speed = 'fast'
        gui.update_speed_display("x2")

    def move_player(event):
        if is_game_over or not player_bot: return
        dx, dy = 0, 0
        if event.keysym == 'Up': dy = -1
        elif event.keysym == 'Down': dy = 1
        elif event.keysym == 'Left': dx = -1
        elif event.keysym == 'Right': dx = 1
        if dx != 0 or dy != 0:
            new_x = (player_bot.x + dx) % grid.width
            new_y = (player_bot.y + dy) % grid.height
            if grid.move_entity(player_bot, new_x, new_y):
                gui.update_display()

    root.bind("<KeyPress-1>", set_normal_speed)
    root.bind("<KeyPress-2>", set_fast_speed)
    root.bind("<KeyPress-Up>", move_player)
    root.bind("<KeyPress-Down>", move_player)
    root.bind("<KeyPress-Left>", move_player)
    root.bind("<KeyPress-Right>", move_player)
    set_normal_speed()

    def simulation_step():
        nonlocal is_game_over
        if is_game_over: return
        game_status = grid.check_game_over()
        if game_status is None:
            grid.update_world()
            gui.update_display()
            root.after(game_speed[current_speed], simulation_step)
        else:
            is_game_over = True
            gui.show_game_over_message(game_status)

    simulation_step()
    root.mainloop()

if __name__ == "__main__":
    main()