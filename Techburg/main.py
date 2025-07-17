# Techburg/main.py
import tkinter as tk
from tkinter import font as tkFont, scrolledtext
from grid import Grid
from agents.survivor_bot import SurvivorBot

class App:
    def __init__(self, master):
        self.master = master
        self.master.title("Techburg AI Simulation")
        self.master.configure(bg="gray10")

        self.SIMULATION_SPEED = 250 
        self.simulation_paused = False
        
        self.top_frame = tk.Frame(self.master, bg="gray10")
        self.top_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        left_frame = tk.Frame(self.top_frame, bg="gray10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        middle_frame = tk.Frame(self.top_frame, bg="gray10")
        middle_frame.pack(side=tk.LEFT, padx=(10, 0), fill=tk.Y)

        right_frame = tk.Frame(self.top_frame, bg="gray10")
        right_frame.pack(side=tk.LEFT, padx=(10, 0), fill=tk.Y)

        tk.Label(middle_frame, text="Activity Log", fg="white", bg="gray10", font=("Helvetica", 12, "bold")).pack(anchor='w')
        self.log_widget = scrolledtext.ScrolledText(middle_frame, width=50, height=30, bg="black", fg="lawn green", font=("Consolas", 9), relief=tk.SUNKEN, borderwidth=1)
        self.log_widget.pack(fill=tk.BOTH, expand=True)
        self.log_widget.configure(state='disabled')
        
        tk.Label(right_frame, text="Color Key", fg="white", bg="gray10", font=("Helvetica", 12, "bold")).pack(anchor='w')
        key_frame = tk.Frame(right_frame, bg="black", relief=tk.SUNKEN, borderwidth=1)
        key_frame.pack(fill=tk.BOTH, expand=True)
        self.create_color_key(key_frame)

        self.GRID_WIDTH, self.GRID_HEIGHT, self.CELL_SIZE = 30, 20, 20
        self.canvas = tk.Canvas(left_frame, width=self.GRID_WIDTH*self.CELL_SIZE, height=self.GRID_HEIGHT*self.CELL_SIZE, bg='black', highlightthickness=0)
        self.canvas.pack()

        status_frame = tk.Frame(left_frame, bg="gray25", relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X, pady=(5,0))
        self.status_text = tk.StringVar()
        self.status_bar = tk.Label(status_frame, textvariable=self.status_text, anchor=tk.W, fg="white", bg="gray25", font=("Consolas", 10), padx=5)
        self.status_bar.pack(fill=tk.X)

        self.create_buttons(left_frame)
        self.start_new_game()

    def create_color_key(self, parent_frame):
        key_entries = [
            ("Survivor Bot", "orange"), ("Gatherer Bot", "light sea green"), ("Repair Bot", "cornflower blue"),
            ("Drone", "red"), ("Swarm", "lawn green"), ("Recharge Station", "purple"),
            ("Speed Part", "light green"), ("Vision Part", "light blue"), ("Energy Part", "orange")
        ]
        title = tk.Label(parent_frame, text="Entities", bg="black", fg="white", font=("Helvetica", 10, "bold"))
        title.pack(pady=(5, 10))
        for text, color in key_entries:
            entry_frame = tk.Frame(parent_frame, bg="black")
            color_box = tk.Label(entry_frame, text="  ", bg=color)
            color_box.pack(side=tk.LEFT, padx=(5, 10))
            label = tk.Label(entry_frame, text=text, bg="black", fg="white")
            label.pack(side=tk.LEFT, anchor='w')
            entry_frame.pack(anchor='w', pady=2)

    def log_message(self, message):
        self.log_widget.configure(state='normal')
        self.log_widget.insert(tk.END, message + "\n")
        self.log_widget.see(tk.END)
        self.log_widget.configure(state='disabled')

    def create_buttons(self, parent_frame):
        button_frame = tk.Frame(parent_frame, bg="gray10"); button_frame.pack(fill=tk.X, pady=5)
        self.pause_button = tk.Button(button_frame, text="Pause", command=self.toggle_pause, width=10); self.pause_button.pack(side=tk.LEFT)
        quit_button = tk.Button(button_frame, text="Quit Game", command=self.master.destroy, bg="dark red", fg="white", activebackground="red"); quit_button.pack(side=tk.RIGHT, padx=5)
        tk.Button(button_frame, text="Try Again", command=self.start_new_game, bg="steel blue", fg="white", activebackground="light blue").pack(side=tk.RIGHT)
        self.master.bind('<space>', self.toggle_pause)

    def start_new_game(self):
        self.simulation_paused = False
        if hasattr(self, 'pause_button'): self.pause_button.config(text="Pause")
        self.log_widget.configure(state='normal'); self.log_widget.delete(1.0, tk.END); self.log_widget.configure(state='disabled')
        
        self.grid = Grid(self.GRID_WIDTH, self.GRID_HEIGHT, self.log_message)
        self.main_bot = self.grid.populate_world(
            num_parts=50, num_stations=5, num_drones=4, 
            num_swarms=3, num_gatherers=6, num_repair_bots=3
        )
        self.initial_survivor_count = len(self.grid.get_all_bots())
        
        self.log_message("--- Simulation Starting ---")
        self.simulation_step()

    def toggle_pause(self, event=None):
        self.simulation_paused = not self.simulation_paused
        self.log_message(f"--- Simulation {'Paused' if self.simulation_paused else 'Resumed'} ---")
        self.pause_button.config(text="Resume" if self.simulation_paused else "Pause")
        if not self.simulation_paused: self.simulation_step()

    def simulation_step(self):
        if self.simulation_paused or 'normal' != self.master.state(): return
        
        # First, update the state of the world
        self.grid.update_world()
        self.draw_grid()
        
        # Now, check for end conditions based on the new state
        game_over = False
        if self.grid.initial_part_count > 0 and self.grid.parts_collected >= self.grid.initial_part_count:
            self.game_won(); game_over = True
        elif not self.main_bot or self.main_bot not in self.grid.entities:
            self.game_over("ENERGY CORE DEPLETED"); game_over = True
        elif not self.grid.get_all_bots():
            self.game_over("All survivor bots were eliminated!"); game_over = True
        
        # If the game is not over, schedule the next step
        if not game_over:
            self.master.after(self.SIMULATION_SPEED, self.simulation_step)

    def draw_grid(self):
        self.canvas.delete("all")
        for x in range(self.GRID_WIDTH):
            for y in range(self.GRID_HEIGHT):
                x1, y1 = x*self.CELL_SIZE, y*self.CELL_SIZE; x2, y2 = x1+self.CELL_SIZE, y1+self.CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="gray25", fill="")
        for entity in self.grid.entities:
            x1, y1 = entity.x*self.CELL_SIZE, entity.y*self.CELL_SIZE; x2, y2 = x1+self.CELL_SIZE, y1+self.CELL_SIZE
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=getattr(entity, 'color', 'white'), outline="")
        self.update_ui()

    def update_ui(self):
        all_bots = self.grid.get_all_bots()
        num_survivors = len(all_bots)
        bots_destroyed = self.initial_survivor_count - num_survivors
        main_bot_energy = int(self.main_bot.energy) if self.main_bot and self.main_bot in all_bots else "---"
        parts_goal = self.grid.initial_part_count
        self.status_text.set(f"Main Bot Energy: {main_bot_energy} | Bots Active: {num_survivors} | Parts Collected: {self.grid.parts_collected}/{parts_goal} | Bots Destroyed: {bots_destroyed}")

    def game_won(self):
        self.log_message("--- SIMULATION SUCCESSFUL ---")
        self.canvas.create_text(self.GRID_WIDTH*self.CELL_SIZE/2, self.GRID_HEIGHT*self.CELL_SIZE/2, text="AI TEAM WINS", font=("Helvetica", 32, "bold"), fill="lawn green")

    def game_over(self, reason=""):
        self.log_message(f"--- SIMULATION FAILED: {reason} ---")
        self.canvas.create_text(self.GRID_WIDTH*self.CELL_SIZE/2, self.GRID_HEIGHT*self.CELL_SIZE/2, text="GAME OVER", font=("Helvetica", 40, "bold"), fill="red")
        if reason:
            self.canvas.create_text(self.GRID_WIDTH*self.CELL_SIZE/2, self.GRID_HEIGHT*self.CELL_SIZE/2 + 25, text=reason, font=("Helvetica", 14), fill="white")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()