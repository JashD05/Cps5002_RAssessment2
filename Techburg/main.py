# File: Techburg/main.py
import tkinter as tk
from grid import Grid
from gui import SimulationGUI
from agents.survivor_bot import PlayerBot

def main():
    """Main function to initialize and run the Techburg simulation."""
    root = tk.Tk()
    root.title("Techburg Simulation")

    # --- Game State Variables ---
    # Defines the delay in milliseconds for each speed setting
    game_speed_options = {'x1': 200, 'x2': 75}
    current_speed_mode = 'x1' # Start at normal speed
    is_game_over = False

    grid = Grid(width=30, height=30)
    gui = SimulationGUI(root, grid)

    # Populate the world and get a reference to the player bot
    grid.populate_world(
        num_gatherer_bots=6,
        num_repair_bots=3,
        num_drones=6,
        num_swarms=4,
        num_parts=70,
        num_recharge_stations=5
    )
    player_bot = [bot for bot in grid.get_all_bots() if isinstance(bot, PlayerBot)][0]


    # --- Key Binding Functions ---
    def set_speed(mode):
        """Sets the game speed and updates the GUI."""
        nonlocal current_speed_mode
        if mode in game_speed_options:
            current_speed_mode = mode
            gui.update_speed_display(mode)
            print(f"Game speed set to {mode}")

    def handle_keypress(event):
        """Handles all key presses for game control."""
        if is_game_over:
            return

        # Game Speed Controls
        if event.keysym == '1':
            set_speed('x1')
        elif event.keysym == '2':
            set_speed('x2')

        # Player Movement Controls
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

    # Bind all key presses to the handler function
    root.bind("<KeyPress>", handle_keypress)
    set_speed('x1') # Set initial speed display

    # --- Main Simulation Loop ---
    def simulation_step():
        nonlocal is_game_over
        if is_game_over: return

        game_status = grid.check_game_over()
        if game_status is None:
            grid.update_world()
            gui.update_display()
            # Schedule the next AI turn using the current speed setting
            root.after(game_speed_options[current_speed_mode], simulation_step)
        else:
            is_game_over = True
            gui.show_game_over_message(game_status)

    simulation_step()
    root.mainloop()

if __name__ == "__main__":
    main()