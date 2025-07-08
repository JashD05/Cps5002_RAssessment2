# File: gui.py

import tkinter as tk

class SimulationGUI:
    """Handles the graphical user interface for the simulation using tkinter."""
    def __init__(self, grid_size=(30, 30), cell_size=20):
        self.grid_width, self.grid_height = grid_size
        self.cell_size = cell_size
        
        self.window = tk.Tk()
        self.window.title("Techburg Simulation")
        
        canvas_width = self.grid_width * self.cell_size
        canvas_height = self.grid_height * self.cell_size
        
        self.canvas = tk.Canvas(self.window, width=canvas_width, height=canvas_height, bg='black')
        self.canvas.pack()
        
        self._draw_grid()

    def _draw_grid(self):
        """Draws the grid lines on the canvas."""
        for i in range(self.grid_width):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.grid_height * self.cell_size, fill='#333')
        for i in range(self.grid_height):
            y = i * self.cell_size
            self.canvas.create_line(0, y, self.grid_width * self.cell_size, y, fill='#333')

    def update_display(self, all_items):
        """Clears and redraws all items on the grid."""
        self.canvas.delete("all_items")
        for item in all_items:
            x, y = item.position
            fill_color = item.color
            
            x1 = x * self.cell_size
            y1 = y * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, tags="all_items")
        
        self.window.update_idletasks()
        self.window.update()