# Techburg/gui.py
import tkinter as tk
from grid import Grid

class TechburgGUI:
    def __init__(self, master, grid):
        self.master = master
        self.grid = grid
        self.cell_size = 20  # Define cell size for drawing

        self.canvas = tk.Canvas(
            master,
            width=self.grid.width * self.cell_size,
            height=self.grid.height * self.cell_size,
            bg='black'
        )
        self.canvas.pack()
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete('all')
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                x1 = x * self.cell_size
                y1 = y * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline='gray', fill='black')

        for entity in self.grid.entities:
            x1 = entity.x * self.cell_size
            y1 = entity.y * self.cell_size
            x2 = x1 + self.cell_size
            y2 = y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=entity.get_color(), outline='gray')

    def update(self):
        self.draw_grid()
        self.master.after(100, self.update)

# This part is for testing the GUI independently. It's not used by main.py.
if __name__ == '__main__':
    root = tk.Tk()
    root.title("Techburg Simulation")
    
    # Use the Grid class from grid.py for consistency
    game_grid = Grid(width=30, height=20) 
    
    # You can add test entities here if you want to test the GUI directly
    # from entities import SparePart
    # game_grid.add_entity(SparePart('small', 5, 5))

    gui = TechburgGUI(root, game_grid)
    gui.update()
    root.mainloop()