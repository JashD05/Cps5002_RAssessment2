# File: gui.py

import tkinter as tk
from grid import Grid

class SimulationGUI:
    def __init__(self, grid: Grid, cell_size=20):
        self.grid = grid
        self.cell_size = cell_size
        self.window = tk.Tk()
        self.window.title("Techburg Simulation")
        
        canvas_width = self.grid.width * self.cell_size
        canvas_height = self.grid.height * self.cell_size
        self.canvas = tk.Canvas(self.window, width=canvas_width, height=canvas_height, bg='black')
        self.canvas.pack()
        
        self._draw_grid_lines()

    def _draw_grid_lines(self):
        for i in range(self.grid.width):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.grid.height * self.cell_size, fill='#333')
        for i in range(self.grid.height):
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.grid.width * self.cell_size, y, fill='#333')

    def update_display(self):
        self.canvas.delete("all_items")
        items_to_draw = self.grid.get_all_entities() + self.grid.get_drawable_stations()
        for item in items_to_draw:
            x, y = item.position
            fill_color = item.color
            x1, y1 = x * self.cell_size, y * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, tags="all_items")
        self.window.update()
        
    def start(self):
        self.window.mainloop()