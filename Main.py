import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import threading

# List to store the history of simulation data
simulation_history = []
# List to store previous positions of the car
previous_positions = []

# Starting position of the car
current_position = (0, 0)
# Target position (Point B)
target_position = (9, 9)

# Function to simulate speed readings
def simulate_sensor_data():
    """Generate a random speed between 0 and 120 km/h."""
    return random.uniform(0, 120)

# Function to check if a crash occurs
def check_for_crash(speed):
    """Determine if a crash happens based on speed and a random chance."""
    return speed > 100 or random.randint(1, 50) == 1  # 1 in 50 chance of crashing

# Function to update the simulation data and check for crashes
def update_data():
    """Run the simulation until the car reaches Point B."""
    global simulation_history, previous_positions, current_position, target_position
    crash_detected = False

    while current_position != target_position:
        speed = simulate_sensor_data()  # Get the current speed
        crash_detected = check_for_crash(speed)  # Check for a crash

        # Log the current data
        status = "Crashed" if crash_detected else "Not Crashed"
        log_entry = {
            "Time": time.strftime("%H:%M:%S"),
            "Speed": f"{speed:.2f} km/h",
            "Coordinates": f"{get_grid_coordinates(current_position)}",
            "Status": status
        }
        simulation_history.append(log_entry)  # Add to history

        # Update the data table with the latest log
        update_table()

        # Store the previous position
        previous_positions.append(current_position)

        # Move the car one step towards the target
        move_car_towards_point_b()

        # Draw lines connecting the previous positions
        draw_connection_lines()

        time.sleep(1)  # Wait for a second before the next update

        if crash_detected:
            messagebox.showinfo("Simulation Result", "Crashed! Simulation stopped.")
            break

    if not crash_detected:
        messagebox.showinfo("Simulation Result", "Reached Point B!")
    
# Function to convert grid position to a readable format
def get_grid_coordinates(position):
    """Convert grid position to a string like 'C-6'."""
    letter = chr(65 + position[0])  # Convert x to a letter (A-J)
    number = position[1] + 1         # Convert y to a number (1-10)
    return f"{letter}-{number}"

# Function to update the data table with the latest logs
def update_table():
    """Refresh the data table with the latest log entries."""
    for row in tree.get_children():
        tree.delete(row)  # Clear the current table

    # Add all log entries to the table
    for entry in simulation_history:
        tree.insert("", "end", values=(entry["Time"], entry["Speed"],
                                        entry["Coordinates"], entry["Status"]))

# Function to update the car's position on the canvas
def update_car_position(position):
    """Move the car to the new position on the grid."""
    global car
    grid_size = 60  # Size of each grid cell
    car_x = position[0] * grid_size + 10  # Calculate x position
    car_y = position[1] * grid_size + 10  # Calculate y position
    canvas.coords(car, car_x, car_y, car_x + 40, car_y + 40)  # Update car rectangle

# Function to move the car one step towards Point B
def move_car_towards_point_b():
    """Move the car one grid space towards Point B."""
    global current_position, target_position

    if current_position != target_position:
        # Move right
        if current_position[0] < target_position[0]:
            current_position = (current_position[0] + 1, current_position[1])
        # Move left
        elif current_position[0] > target_position[0]:
            current_position = (current_position[0] - 1, current_position[1])
        # Move down
        elif current_position[1] < target_position[1]:
            current_position = (current_position[0], current_position[1] + 1)
        # Move up
        elif current_position[1] > target_position[1]:
            current_position = (current_position[0], current_position[1] - 1)

        update_car_position(current_position)  # Update the car's position on the canvas

# Function to start the simulation in a separate thread
def start_simulation():
    """Begin the simulation in a new thread to keep the interface responsive."""
    threading.Thread(target=update_data, daemon=True).start()

# Set up the main application window
root = tk.Tk()
root.title("Smart Car Crash Detection System")

# Create a canvas for the grid
canvas = tk.Canvas(root, width=600, height=600, bg="skyblue")
canvas.pack()

# Create the grid
for i in range(10):
    for j in range(10):
        canvas.create_rectangle(i * 60, j * 60, (i + 1) * 60, (j + 1) * 60, outline="white")

# Create the car representation
car = canvas.create_rectangle(10, 10, 50, 50, fill="red")

# Create a button to start the simulation
start_button = tk.Button(root, text="Start Simulation", command=start_simulation)
start_button.pack()

# Create a treeview to display the logs
tree = ttk.Treeview(root, columns=("Time", "Speed", "Coordinates", "Status"), show="headings")
tree.heading("Time", text="Time")
tree.heading("Speed", text="Speed")
tree.heading("Coordinates", text="Coordinates")
tree.heading("Status", text="Status")
tree.pack()

# Start the Tkinter main loop
root.mainloop()
