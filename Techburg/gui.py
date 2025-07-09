# File: Techburg/gui.py
import tkinter as tk
from tkinter import font

class SimulationGUI:
    def __init__(self, master, grid, cell_size=20):
        self.master = master
        self.grid = grid
        self.cell_size = cell_size
        self.window = master
        self.canvas = tk.Canvas(self.window, width=grid.width * self.cell_size, height=grid.height * self.cell_size, bg='black', highlightthickness=0)
        self.canvas.pack(pady=10, padx=10)

        info_frame = tk.Frame(self.window, bg='grey10')
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.status_font = font.Font(family="Consolas", size=10)

        self.status_label = tk.Label(info_frame, text="Player: Energy=100%", bg='grey10', fg='white', font=self.status_font)
        self.stats_label = tk.Label(info_frame, text="Bots: 0 | Parts: 0/0", bg='grey10', fg='cyan', font=self.status_font)

        # --- NEW: Speed Display Label ---
        self.speed_label = tk.Label(info_frame, text="Speed: x1", bg='grey10', fg='yellow', font=self.status_font)
        # --- END NEW ---

        self.quit_button = tk.Button(info_frame, text="Quit Game", command=self.master.destroy, bg="red4", fg="white", font=self.status_font, relief=tk.FLAT, padx=10)

        # Pack elements into the info frame
        self.status_label.pack(side=tk.LEFT, padx=10, pady=5)
        self.stats_label.pack(side=tk.LEFT, expand=True, fill=tk.X, pady=5)
        self.speed_label.pack(side=tk.LEFT, padx=10, pady=5) # Add speed label to the bar
        self.quit_button.pack(side=tk.RIGHT, padx=10, pady=5)


    def update_display(self):
        self.canvas.delete("all")
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                entity = self.grid.get_entity(x, y)
                x1, y1 = x * self.cell_size, y * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                fill_color = entity.color if hasattr(entity, 'color') else 'black'
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline='grey25')
        self._update_stats_panel()
        self.window.update()

    # --- NEW: Method to update the speed text ---
    def update_speed_display(self, speed_text):
        """Updates the speed label with the current setting."""
        self.speed_label.config(text=f"Speed: {speed_text}")
    # --- END NEW ---

    def show_game_over_message(self, status):
        message = "YOU WIN! 🎉" if status == "win" else "GAME OVER"
        fill_color = "green" if status == "win" else "red"
        canvas_width = self.grid.width * self.cell_size
        canvas_height = self.grid.height * self.cell_size
        self.canvas.create_rectangle(0, canvas_height/2 - 50, canvas_width, canvas_height/2 + 50, fill="black", outline="")
        self.canvas.create_text(canvas_width / 2, canvas_height / 2, text=message, font=("Consolas", 60, "bold"), fill=fill_color)
        self.window.update()

    def _update_stats_panel(self):
        bot_count = len(self.grid.get_all_bots())
        parts_collected = self.grid.get_parts_collected_count()
        total_parts = self.grid.get_initial_parts_count()
        bots_destroyed = self.grid.get_bots_destroyed_count()
        stats_text = (f"Bots Active: {bot_count} | Parts Collected: {parts_collected}/{total_parts} | Bots Destroyed: {bots_destroyed}")
        self.stats_label.config(text=stats_text)