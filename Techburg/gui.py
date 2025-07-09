# File: gui.py
import tkinter as tk
from tkinter import font

class SimulationGUI:
    """Handles the graphical user interface for the Techburg simulation."""
    def __init__(self, master, grid, cell_size=20):
        self.master = master
        self.grid = grid
        self.cell_size = cell_size
        self.window = master
        self.canvas = tk.Canvas(
            self.window,
            width=grid.width * self.cell_size,
            height=grid.height * self.cell_size,
            bg='black'
        )
        self.canvas.pack(pady=10, padx=10)

        info_frame = tk.Frame(self.window, bg='grey10')
        info_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        self.status_font = font.Font(family="Consolas", size=10)
        self.status_label = tk.Label(info_frame, text="Player: Energy=100%", bg='grey10', fg='white', font=self.status_font)
        self.stats_label = tk.Label(info_frame, text="Bots: 0 | Parts: 0/0", bg='grey10', fg='cyan', font=self.status_font)
        self.status_label.pack(side=tk.LEFT, padx=10)
        self.stats_label.pack(side=tk.RIGHT, padx=10)

    def update_display(self):
        """Redraws the canvas and updates the information labels."""
        self.canvas.delete("all")
        for entity in self.grid.entities:
            x1 = entity.x * self.cell_size
            y1 = entity.y * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=entity.color, outline='grey20')
        self._update_stats_panel()
        self.window.update()

    def _update_stats_panel(self):
        """Updates the text in the simulation statistics panel."""
        bot_count = len(self.grid.get_all_bots())
        parts_collected = self.grid.get_parts_collected_count()
        total_parts = self.grid.get_initial_parts_count()
        bots_destroyed = self.grid.get_bots_destroyed_count()

        stats_text = (f"Bots Active: {bot_count} | "
                      f"Parts Collected: {parts_collected}/{total_parts} | "
                      f"Bots Destroyed: {bots_destroyed}")
        self.stats_label.config(text=stats_text)