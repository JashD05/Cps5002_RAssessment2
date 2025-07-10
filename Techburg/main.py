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
    global grid, player_bot, window, canvas, status_bar, initial_survivor_count, simulation_paused, pause_button

    simulation_paused = False

    grid = Grid(GRID_WIDTH, GRID_HEIGHT)
    
    player_bot = grid.populate_world(
        num_parts=50,
        num_stations=5,
        num_drones=6,
        num_swarms=4,
        num_gatherers=6,
        num_repair_bots=3
    )
    
    initial_survivor_count = len(grid.get_all_bots())
            
    # --- GUI Setup ---
    window = tk.Tk()
    window.title("Techburg Simulation")
    window.configure(bg="gray10")
    
    main_frame = tk.Frame(window, bg="gray10"); main_frame.pack(padx=10, pady=10)
    canvas = tk.Canvas(main_frame, width=GRID_WIDTH*CELL_SIZE, height=GRID_HEIGHT*CELL_SIZE, bg='black', highlightthickness=0); canvas.pack()
    status_frame = tk.Frame(main_frame, bg="gray25", relief=tk.SUNKEN, borderwidth=1); status_frame.pack(fill=tk.X, pady=(5,0))
    status_text = tk.StringVar()
    status_bar = tk.Label(status_frame, textvariable=status_text, anchor=tk.W, fg="white", bg="gray25", font=("Consolas", 10), padx=5); status_bar.pack(fill=tk.X)
    status_bar.text_var = status_text

    button_frame = tk.Frame(main_frame, bg="gray10"); button_frame.pack(fill=tk.X, pady=5)
    pause_button = tk.Button(button_frame, text="Pause", command=toggle_pause, width=10); pause_button.pack(side=tk.LEFT)
    quit_button = tk.Button(button_frame, text="Quit Game", command=window.destroy, bg="dark red", fg="white", activebackground="red"); quit_button.pack(side=tk.RIGHT, padx=5)
    tk.Button(button_frame, text="Try Again", command=lambda: restart_program(window), bg="steel blue", fg="white", activebackground="light blue").pack(side=tk.RIGHT)

    window.bind('<KeyPress-w>', lambda e: move_player(0, -1)); window.bind('<KeyPress-s>', lambda e: move_player(0, 1))
    window.bind('<KeyPress-a>', lambda e: move_player(-1, 0)); window.bind('<KeyPress-d>', lambda e: move_player(1, 0))
    window.bind('<space>', toggle_pause)

    simulation_step()
    window.mainloop()

def toggle_pause(event=None):
    """Pauses or resumes the simulation."""
    global simulation_paused
    simulation_paused = not simulation_paused
    pause_button.config(text="Resume" if simulation_paused else "Pause")
    if not simulation_paused: simulation_step()

def restart_program(window): window.destroy(); main()

def move_player(dx, dy):
    """Moves the player bot."""
    if not simulation_paused and player_bot and player_bot.energy > 0:
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
    if simulation_paused or 'normal' != window.state(): return
    
    # --- Check for end conditions ---
    # Win Condition
    if grid.initial_part_count > 0 and grid.parts_collected >= grid.initial_part_count:
        draw_grid()
        game_won()
        return

    # **FIX:** Lose condition is now specifically when the player's energy is zero or less.
    if player_bot.energy <= 0:
        draw_grid()
        game_over()
        return

    # If game is not over, continue
    grid.update_world()
    draw_grid()
    window.after(SIMULATION_SPEED, simulation_step)

def draw_grid():
    """Draws the grid and all entities."""
    canvas.delete("all")
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            x1, y1 = x*CELL_SIZE, y*CELL_SIZE; x2, y2 = x1+CELL_SIZE, y1+CELL_SIZE
            canvas.create_rectangle(x1, y1, x2, y2, outline="gray25", fill="")
    for entity in grid.entities:
        x1, y1 = entity.x*CELL_SIZE, entity.y*CELL_SIZE; x2, y2 = x1+CELL_SIZE, y1+CELL_SIZE
        canvas.create_rectangle(x1, y1, x2, y2, fill=getattr(entity, 'color', 'white'), outline="")
    update_ui()

def update_ui():
    """Updates the consolidated status bar."""
    all_bots = grid.get_all_bots()
    num_survivors = len(all_bots)
    bots_destroyed = initial_survivor_count - num_survivors
    
    # The player object is always available, even if its energy is <= 0
    player_energy = int(player_bot.energy)
    
    parts_goal = grid.initial_part_count
    status_string = (f"Player: Energy={player_energy} | Bots Active: {num_survivors} | Parts Collected: {grid.parts_collected}/{parts_goal} | Bots Destroyed: {bots_destroyed}")
    status_bar.text_var.set(status_string)

def game_won():
    """Displays a 'You Win!' message on the canvas."""
    bold_font = tkFont.Font(family="Helvetica", size=40, weight="bold")
    canvas.create_text(GRID_WIDTH * CELL_SIZE / 2, GRID_HEIGHT * CELL_SIZE / 2, text="YOU WIN!", font=bold_font, fill="lawn green")

def game_over():
    """Displays a 'Game Over' message on the canvas."""
    bold_font = tkFont.Font(family="Helvetica", size=40, weight="bold")
    canvas.create_text(GRID_WIDTH*CELL_SIZE/2, GRID_HEIGHT*CELL_SIZE/2, text="GAME OVER", font=bold_font, fill="red")

if __name__ == "__main__":
    main()