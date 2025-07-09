# File: test_gui.py

import tkinter as tk
import time

print("--- Starting GUI Test ---")

try:
    print("Creating Tkinter window...")
    window = tk.Tk()
    window.title("Test Window")
    window.geometry("400x200")

    label = tk.Label(window, text="If this window stays open, Tkinter is working.", font=("Helvetica", 14))
    label.pack(pady=40)

    print("Starting mainloop... The window should appear now.")
    window.mainloop()
    
    # This line will only run after you manually close the window
    print("Mainloop finished. Test successful!")

except Exception as e:
    print("\n--- AN ERROR OCCURRED ---")
    print(f"Error details: {e}")