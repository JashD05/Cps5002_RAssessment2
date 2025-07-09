# File: main.py
import tkinter as tk
from grid import Grid
from gui import SimulationGUI  # This line must match the class name in gui.py

def main():
    """Main function to initialize and run the Techburg simulation."""
    root = tk.Tk()
    root.title("Techburg Simulation")

    grid = Grid(width=30, height=30)
    gui = SimulationGUI(root, grid) # This line must also match

    # --- Simulation Setup ---
    grid.populate_world(
        num_gatherer_bots=4,
        num_repair_bots=2,
        num_drones=3,
        num_swarms=2,
        num_parts=50,
        num_recharge_stations=5
    )

    # --- Main Simulation Loop ---
    def simulation_step():
        grid.update_world()
        gui.update_display()
        root.after(200, simulation_step)

    # Start the simulation
    simulation_step()
    root.mainloop()

if __name__ == "__main__":
    main()