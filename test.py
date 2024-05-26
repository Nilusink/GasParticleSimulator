import tkinter as tk
from tkinter import messagebox

# Constants
R = 0.0821  # Ideal gas constant in L·atm/(mol·K)


def calculate_moles():
    try:
        P = float(entry_pressure.get())
        V = float(entry_volume.get())
        T = float(entry_temperature.get())

        if T <= 0:
            messagebox.showerror("Input Error", "Temperature must be greater than 0 K")
            return

        n = (P * V) / (R * T)
        result_label.config(text=f"Number of moles (n): {n:.4f} mol")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for all fields")


# Set up the main application window
root = tk.Tk()
root.title("Ideal Gas Law Simulator")

# Create and place the labels and entries for pressure, volume, and temperature
tk.Label(root, text="Pressure (P) in atm:").grid(row=0, column=0, padx=10, pady=10)
entry_pressure = tk.Entry(root)
entry_pressure.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="Volume (V) in L:").grid(row=1, column=0, padx=10, pady=10)
entry_volume = tk.Entry(root)
entry_volume.grid(row=1, column=1, padx=10, pady=10)

tk.Label(root, text="Temperature (T) in K:").grid(row=2, column=0, padx=10, pady=10)
entry_temperature = tk.Entry(root)
entry_temperature.grid(row=2, column=1, padx=10, pady=10)

# Create and place the calculate button
calculate_button = tk.Button(root, text="Calculate Moles", command=calculate_moles)
calculate_button.grid(row=3, column=0, columnspan=2, pady=20)

# Create and place the result label
result_label = tk.Label(root, text="Number of moles (n): ")
result_label.grid(row=4, column=0, columnspan=2, pady=10)

# Run the main event loop
root.mainloop()
