# main.py
import tkinter as tk
from tkinter import font as tkFont
import random
import sys
import os
from grid import Grid
from agents.survivor_bot import PlayerBot, GathererBot, RepairBot, SurvivorBot

# --- Simulation Parameters ---
GRID_WIDTH = 30
GRID_HEIGHT = 20
CELL_SIZE = 20
SIMULATION_SPEED = 100

def main():
    """Sets up and runs the simulation."""
    global grid, player_bot, window, canvas, status_bar, initial_survivor_count

    grid = Grid(GRID_WIDTH, GRID_HEIGHT)
    
    player_bot = grid.populate_world(
        num_parts=70,
        num_stations=5,
        num_drones=6,
        num_swarms=4,
        num_gatherers=6,
        num_repair_bots=3
    )
    
    initial_survivor_count = len([e for e in grid.entities if isinstance(e, SurvivorBot)])
            
    # --- GUI Setup ---
    window = tk.Tk()
    window.title("Techburg Simulation")
    window.configure(bg="gray10")
    
    main_frame = tk.Frame(window, bg="gray10")
    main_frame.pack(padx=10, pady=10)

    canvas = tk.Canvas(main_frame, width=GRID_WIDTH * CELL_SIZE, height=GRID_HEIGHT * CELL_SIZE, bg='black', highlightthickness=0)
    canvas.pack()

    status_frame = tk.Frame(main_frame, bg="gray25", relief=tk.SUNKEN, borderwidth=1)
    status_frame.pack(fill=tk.X, pady=(5,0))

    status_text = tk.StringVar()
    status_font = tkFont.Font(family="Consolas", size=10)
    status_bar = tk.Label(status_frame, textvariable=status_text, anchor=tk.W, fg="white", bg="gray25", font=status_font, padx=5)
    status_bar.pack(fill=tk.X)
    status_bar.text_var = status_text

    button_frame = tk.Frame(main_frame, bg="gray10")
    button_frame.pack(fill=tk.X, pady=5)
    
    quit_button = tk.Button(button_frame, text="Quit Game", command=window.destroy, bg="dark red", fg="white", activebackground="red")
    quit_button.pack(side=tk.RIGHT, padx=5)
    
    try_again_button = tk.Button(button_frame, text="Try Again", command=lambda: restart_program(window), bg="steel blue", fg="white", activebackground="light blue")
    try_again_button.pack(side=tk.RIGHT)

    window.bind('<KeyPress-w>', lambda event: move_player(0, -1))
    window.bind('<KeyPress-s>', lambda event: move_player(0, 1))
    window.bind('<KeyPress-a>', lambda event: move_player(-1, 0))
    window.bind('<KeyPress-d>', lambda event: move_player(1, 0))

    simulation_step()
    window.mainloop()

def restart_program(window):
    """Restarts the current program."""
    window.destroy()
    main()

def move_player(dx, dy):
    """Moves the player bot and checks for part collection."""
    if player_bot and player_bot.energy > 0:
        new_x, new_y = player_bot.x + dx, player_bot.y + dy
        if grid.is_valid(new_x, new_y):
            entity_at_new_pos = grid.get_entity(new_x, new_y)
            if not entity_at_new_pos or entity_at_new_pos.type in ['spare_part', 'recharge_station']:
                grid.move_entity(player_bot, new_x, new_y)
                
                part_to_collect = grid.get_entity(new_x, new_y)
                if part_to_collect and part_to_collect.type == 'spare_part':
                    player_bot.pickup_part(part_to_collect, grid)

def simulation_step():
    """Runs one step of the simulation and schedules the next."""
    if 'normal' != window.state(): return
    
    if player_bot and player_bot in grid.entities:
        grid.update_world()
        draw_grid()
        window.after(SIMULATION_SPEED, simulation_step)
    else:
        draw_grid()
        game_over()

def draw_grid():
    """Draws the grid and all entities."""
    canvas.delete("all")
    
    # --- DEBUG SECTION ---
    print("\n--- Drawing Frame ---")
    for i, entity in enumerate(grid.entities):
        if i < 5: # Limit to first 5 entities to avoid spamming the console
            print(f"[DEBUG] Drawing {entity.type:<15} at (x={entity.x}, y={entity.y})")
    # --- END DEBUG ---

    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            x1, y1 = x * CELL_SIZE, y * CELL_SIZE
            x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
            canvas.create_rectangle(x1, y1, x2, y2, outline="gray25", fill="")

    for entity in grid.entities:
        x1, y1 = entity.x * CELL_SIZE, entity.y * CELL_SIZE
        x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
        entity_color = getattr(entity, 'color', 'white')
        canvas.create_rectangle(x1, y1, x2, y2, fill=entity_color, outline="")
    
    update_ui()

def update_ui():
    """Updates the consolidated status bar."""
    current_survivors = [e for e in grid.entities if isinstance(e, SurvivorBot)]
    num_survivors = len(current_survivors)
    bots_destroyed = initial_survivor_count - num_survivors
    
    player_energy = int(player_bot.energy) if player_bot and player_bot in grid.entities else "---"
    parts_collected = grid.parts_collected
    
    status_string = (f"Player: Energy={player_energy} | "
                     f"Bots Active: {num_survivors} | "
                     f"Parts Collected: {parts_collected}/50 | "
                     f"Bots Destroyed: {bots_destroyed}")
    
    status_bar.text_var.set(status_string)

def game_over():
    """Displays a game over message on the canvas."""
    bold_font = tkFont.Font(family="Helvetica", size=40, weight="bold")
    canvas.create_text(
        GRID_WIDTH * CELL_SIZE / 2, 
        GRID_HEIGHT * CELL_SIZE / 2, 
        text="GAME OVER", 
        font=bold_font,
        fill="red"
    )

if __name__ == "__main__":
    main()