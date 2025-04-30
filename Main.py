import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import threading
from datetime import datetime
import json
import os

EMERGENCY_CONTACTS = ["112", "911", "123-456-7890"]
CONFIRMATION_TIME = 2
GRID_SIZE = 60
CAR_SIZE = 40
MAX_SPEED = 120
ACCELERATION = 20
DECELERATION = 30
HISTORY_FILE = "crash_history.json"

simulation_history = []
current_position = [0, 0]
target_position = (9, 9)
simulation_active = False
obstacles = []
crash_detected = False
current_speed = 0
target_speed = 0
last_update_time = time.time()
speed_at_impact = 0

class VehicleSensors:
    def __init__(self):
        self.speed = 0
        self.crash_status = False

    def update(self, crashed=False):
        global current_speed, speed_at_impact
        self.crash_status = crashed
        if crashed:
            speed_at_impact = current_speed
            current_speed = 0
            self.speed = 0
            return True, "obstacle collision"
        else:
            self.speed = current_speed
            return False, None

def update_speed():
    global current_speed, last_update_time
    now = time.time()
    elapsed = now - last_update_time
    last_update_time = now

    if current_speed < target_speed:
        current_speed = min(target_speed, current_speed + ACCELERATION * elapsed)
    elif current_speed > target_speed:
        current_speed = max(target_speed, current_speed - DECELERATION * elapsed)

def emergency_protocol(crash_type):
    global crash_detected, target_speed
    crash_detected = True
    target_speed = 0
    location = f"{get_grid_coordinates(current_position)}"

    log_entry = {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Speed": f"{speed_at_impact:.1f} km/h",
        "Event": f"CRASH CONFIRMED - {crash_type.upper()}",
        "Location": location,
        "Action": f"Alerted {len(EMERGENCY_CONTACTS)} contacts"
    }
    simulation_history.append(log_entry)
    save_history(log_entry)
    update_table()

    messagebox.showwarning(
        "CRASH DETECTED!",
        f"Emergency alert sent!\n\n"
        f"Crash Type: {crash_type}\n"
        f"Speed at impact: {speed_at_impact:.1f} km/h\n"
        f"Location: {location}\n"
        f"Emergency contacts notified: {', '.join(EMERGENCY_CONTACTS)}"
    )
    return True

def update_car_position():
    global crash_detected

    update_speed()

    car_x = current_position[0] * GRID_SIZE + 10
    car_y = current_position[1] * GRID_SIZE + 10
    canvas.coords(car, car_x, car_y, car_x + CAR_SIZE, car_y + CAR_SIZE)

    if check_collision(current_position) and not crash_detected:
        crash_detected = True
        sensors = VehicleSensors()
        sensors.update(crashed=True)
        emergency_protocol("obstacle collision")

    if tuple(current_position) == target_position and not crash_detected:
        destination_reached()

def destination_reached():
    messagebox.showinfo("Destination Reached 🎉", "\n\nYou have reached your destination safely!")

def save_history(entry):
    history = load_history()
    history.append(entry)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def show_history():
    history = load_history()
    history_window = tk.Toplevel(root)
    history_window.title("Crash History")
    history_window.geometry("800x600")

    if not history:
        tk.Label(history_window, text="No crash history available", font=('Arial', 14)).pack(pady=20)
        return

    tree = ttk.Treeview(history_window, columns=("Time", "Speed", "Location", "Event"), show="headings")
    tree.heading("Time", text="Time")
    tree.heading("Speed", text="Speed (km/h)")
    tree.heading("Location", text="Location")
    tree.heading("Event", text="Event")

    tree.column("Time", width=200)
    tree.column("Speed", width=100)
    tree.column("Location", width=200)
    tree.column("Event", width=300)

    for entry in reversed(history):
        tree.insert("", "end", values=(
            entry.get("Time", ""),
            entry.get("Speed", ""),
            entry.get("Location", ""),
            entry.get("Event", "")
        ))

    scrollbar = ttk.Scrollbar(history_window, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    tree.pack(fill="both", expand=True)

def check_collision(pos):
    car_x1, car_y1 = pos[0] * GRID_SIZE + 10, pos[1] * GRID_SIZE + 10
    car_x2, car_y2 = car_x1 + CAR_SIZE, car_y1 + CAR_SIZE

    for obstacle in obstacles:
        obs_x1, obs_y1 = obstacle[0] * GRID_SIZE, obstacle[1] * GRID_SIZE
        obs_x2, obs_y2 = obs_x1 + GRID_SIZE, obs_y1 + GRID_SIZE

        if (car_x1 < obs_x2 and car_x2 > obs_x1 and 
            car_y1 < obs_y2 and car_y2 > obs_y1):
            return True
    return False

def get_grid_coordinates(position):
    letter = chr(65 + position[0])
    number = position[1] + 1
    return f"{letter}-{number}"

def update_table():
    for row in tree.get_children():
        tree.delete(row)

    for entry in simulation_history:
        values = (
            entry.get("Time", ""),
            entry.get("Speed", ""),
            entry.get("Coordinates", ""),
            entry.get("Status", ""),
            entry.get("Event", ""),
            entry.get("Action", "")
        )
        tree.insert("", "end", values=values)

def update_car_position():
    global crash_detected

    update_speed()

    car_x = current_position[0] * GRID_SIZE + 10
    car_y = current_position[1] * GRID_SIZE + 10
    canvas.coords(car, car_x, car_y, car_x + CAR_SIZE, car_y + CAR_SIZE)

    if check_collision(current_position) and not crash_detected:
        crash_detected = True
        sensors = VehicleSensors()
        sensors.update(crashed=True)
        emergency_protocol("obstacle collision")

    if tuple(current_position) == target_position and not crash_detected:
        destination_reached()

def move_car(direction):
    global current_position, crash_detected, target_speed

    if crash_detected or not simulation_active:
        return

    new_position = current_position.copy()

    if direction == "up" and current_position[1] > 0:
        new_position[1] -= 1
    elif direction == "down" and current_position[1] < 9:
        new_position[1] += 1
    elif direction == "left" and current_position[0] > 0:
        new_position[0] -= 1
    elif direction == "right" and current_position[0] < 9:
        new_position[0] += 1
    else:
        return

    target_speed = MAX_SPEED
    current_position = new_position

    sensors = VehicleSensors()
    is_crash, crash_type = sensors.update(False)

    log_entry = {
        "Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Speed": f"{current_speed:.1f} km/h",
        "Coordinates": get_grid_coordinates(current_position),
        "Status": "Crashed" if crash_detected else "Normal",
        "Event": "Movement",
        "Action": "Accelerating" if target_speed > current_speed else "Decelerating" if target_speed < current_speed else "Maintaining speed"
    }
    simulation_history.append(log_entry)
    update_table()
    update_car_position()

def create_obstacles():
    global obstacles, crash_detected
    obstacles = []
    crash_detected = False
    canvas.delete("obstacle")

    for _ in range(random.randint(5, 8)):
        while True:
            x, y = random.randint(0, 9), random.randint(0, 9)
            if (x, y) != (0, 0) and (x, y) != (9, 9) and (x, y) not in obstacles:
                obstacles.append((x, y))
                canvas.create_rectangle(
                    x * GRID_SIZE, y * GRID_SIZE,
                    (x + 1) * GRID_SIZE, (y + 1) * GRID_SIZE,
                    fill="red", tags="obstacle"
                )
                break

def start_simulation():
    global simulation_active, current_position, crash_detected, current_speed, target_speed
    current_position = [0, 0]
    crash_detected = False
    current_speed = 0
    target_speed = 0
    simulation_history.clear()
    simulation_active = True

    show_simulation_screen()

    for row in tree.get_children():
        tree.delete(row)

    create_obstacles()
    update_car_position()

def show_main_menu():
    for widget in root.winfo_children():
        widget.pack_forget()

    tk.Label(root, text="Smart Car Crash Detection System", font=('Arial', 20)).pack(pady=50)
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=20)

    tk.Button(btn_frame, text="Start Simulation", command=start_simulation, width=20, height=2).pack(pady=10)
    tk.Button(btn_frame, text="View Crash History", command=show_history, width=20, height=2).pack(pady=10)
    tk.Button(btn_frame, text="Exit", command=root.quit, width=20, height=2).pack(pady=10)

def show_simulation_screen():
    global canvas, tree, car

    for widget in root.winfo_children():
        widget.pack_forget()

    canvas = tk.Canvas(root, width=600, height=600, bg="skyblue")
    canvas.pack()

    for i in range(10):
        for j in range(10):
            canvas.create_rectangle(
                i * GRID_SIZE, j * GRID_SIZE,
                (i + 1) * GRID_SIZE, (j + 1) * GRID_SIZE,
                outline="white"
            )

    car = canvas.create_rectangle(
        10, 10, 10 + CAR_SIZE, 10 + CAR_SIZE,
        fill="blue", tags="car"
    )

    canvas.create_rectangle(
        9 * GRID_SIZE + 10, 9 * GRID_SIZE + 10,
        9 * GRID_SIZE + 10 + CAR_SIZE, 9 * GRID_SIZE + 10 + CAR_SIZE,
        fill="green", tags="target"
    )

    control_frame = tk.Frame(root)
    control_frame.pack()
    tk.Button(control_frame, text="Main Menu", command=show_main_menu).grid(row=0, column=0)
    tk.Button(control_frame, text="↑", command=lambda: move_car("up")).grid(row=1, column=1)
    tk.Button(control_frame, text="←", command=lambda: move_car("left")).grid(row=2, column=0)
    tk.Button(control_frame, text="→", command=lambda: move_car("right")).grid(row=2, column=2)
    tk.Button(control_frame, text="↓", command=lambda: move_car("down")).grid(row=2, column=1)

    tree = ttk.Treeview(root, columns=("Time", "Speed", "Coordinates", "Status", "Event", "Action"), show="headings")
    tree.heading("Time", text="Time")
    tree.heading("Speed", text="Speed (km/h)")
    tree.heading("Coordinates", text="Coordinates")
    tree.heading("Status", text="Status")
    tree.heading("Event", text="Event")
    tree.heading("Action", text="Action")

    for col in ("Time", "Speed", "Coordinates", "Status", "Event", "Action"):
        tree.column(col, width=100)

    tree.pack()

    root.bind("<Up>", lambda e: move_car("up"))
    root.bind("<Down>", lambda e: move_car("down"))
    root.bind("<Left>", lambda e: move_car("left"))
    root.bind("<Right>", lambda e: move_car("right"))

root = tk.Tk()
root.title("Smart Car Crash Detection System")
show_main_menu()
root.mainloop()