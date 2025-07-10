# main.py
import tkinter as tk
from tkinter import font as tkFont
import random
from grid import Grid
from agents.survivor_bot import PlayerBot, GathererBot, RepairBot, SurvivorBot

GRID_WIDTH, GRID_HEIGHT, CELL_SIZE = 30, 20, 20
SPEED_LEVELS = [("x0.5", 200), ("x1", 100), ("x2", 50), ("x4", 20)]
simulation_paused, current_speed_index = False, 1

def main():
    global grid, player_bot, window, canvas, status_bar, initial_survivor_count, speed_label, pause_button

    grid = Grid(GRID_WIDTH, GRID_HEIGHT)
    player_bot = grid.populate_world(num_parts=70, num_stations=5, num_drones=6, num_swarms=4, num_gatherers=6, num_repair_bots=3)
    initial_survivor_count = len(grid.get_all_bots())
            
    window = tk.Tk()
    window.title("Techburg Simulation")
    window.configure(bg="gray10")
    
    main_frame = tk.Frame(window, bg="gray10"); main_frame.pack(padx=10, pady=10)
    canvas = tk.Canvas(main_frame, width=GRID_WIDTH*CELL_SIZE, height=GRID_HEIGHT*CELL_SIZE, bg='black', highlightthickness=0); canvas.pack()
    status_frame = tk.Frame(main_frame, bg="gray25", relief=tk.SUNKEN, borderwidth=1); status_frame.pack(fill=tk.X, pady=(5,0))
    status_text = tk.StringVar()
    status_bar = tk.Label(status_frame, textvariable=status_text, anchor=tk.W, fg="white", bg="gray25", font=("Consolas", 10), padx=5); status_bar.pack(fill=tk.X)
    status_bar.text_var = status_text

    control_frame = tk.Frame(main_frame, bg="gray10"); control_frame.pack(fill=tk.X, pady=5)
    pause_button = tk.Button(control_frame, text="Pause", command=toggle_pause, width=10); pause_button.pack(side=tk.LEFT, padx=(0,10))
    tk.Button(control_frame, text="Slower <<", command=lambda: change_speed(-1)).pack(side=tk.LEFT)
    speed_label = tk.Label(control_frame, text=f"Speed: {SPEED_LEVELS[current_speed_index][0]}", width=10, fg="white", bg="gray10"); speed_label.pack(side=tk.LEFT)
    tk.Button(control_frame, text=">> Faster", command=lambda: change_speed(1)).pack(side=tk.LEFT)
    quit_button = tk.Button(control_frame, text="Quit Game", command=window.destroy, bg="dark red", fg="white", activebackground="red"); quit_button.pack(side=tk.RIGHT, padx=5)
    tk.Button(control_frame, text="Try Again", command=lambda: restart_program(window), bg="steel blue", fg="white", activebackground="light blue").pack(side=tk.RIGHT)

    window.bind('<KeyPress-w>', lambda e: move_player(0, -1)); window.bind('<KeyPress-s>', lambda e: move_player(0, 1))
    window.bind('<KeyPress-a>', lambda e: move_player(-1, 0)); window.bind('<KeyPress-d>', lambda e: move_player(1, 0))
    window.bind('<space>', toggle_pause)

    simulation_step()
    window.mainloop()

def change_speed(delta):
    global current_speed_index
    current_speed_index = max(0, min(len(SPEED_LEVELS) - 1, current_speed_index + delta))
    speed_label.config(text=f"Speed: {SPEED_LEVELS[current_speed_index][0]}")

def toggle_pause(event=None):
    global simulation_paused
    simulation_paused = not simulation_paused
    pause_button.config(text="Resume" if simulation_paused else "Pause")
    if not simulation_paused: simulation_step()

def restart_program(window): window.destroy(); main()

def move_player(dx, dy):
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
    if simulation_paused or 'normal' != window.state(): return
    if not (player_bot and player_bot in grid.entities):
        draw_grid(); game_over()
        return

    grid.update_world(); draw_grid()
    window.after(SPEED_LEVELS[current_speed_index][1], simulation_step)

def draw_grid():
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
    num_survivors = len(grid.get_all_bots())
    bots_destroyed = initial_survivor_count - num_survivors
    player_energy = int(player_bot.energy) if player_bot and player_bot in grid.entities else "---"
    status_string = (f"Player: Energy={player_energy} | Bots Active: {num_survivors} | Parts Collected: {grid.parts_collected}/50 | Bots Destroyed: {bots_destroyed}")
    status_bar.text_var.set(status_string)

def game_over():
    canvas.create_text(GRID_WIDTH*CELL_SIZE/2, GRID_HEIGHT*CELL_SIZE/2, text="GAME OVER", font=("Helvetica", 40, "bold"), fill="red")

if __name__ == "__main__":
    main()