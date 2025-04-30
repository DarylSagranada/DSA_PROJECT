# DSA_PROJECT: Smart Car Crash Detection and Emergency Alert System

#Project Members:
1. Jones Latras 
2. Keisha Terece Gibertas
3. Daryl Sagranada

#Description:
This project simulates a low-cost crash detection and emergency alert system using simplified software-only methods. Instead of using real-world sensors, the simulation models accelerometer, gyroscope, and GPS behavior to mimic car movement and crash scenarios. It aims to demonstrate how low-cost, energy-efficient systems can be used in real-world situations—especially by students or individuals seeking affordable safety features.

#How It Works:

• Sensor Data Simulation and Analysis
• The simulation periodically generates and tracks values that represent:
• Acceleration changes, to simulate sudden stops or impacts.
• GPS-like coordinates on a 10x10 grid to simulate vehicle movement and determine a crash site.


These simulated values are stored in an array, with new data continuously compared to older entries. For now the system identifies as over speeding as possible crash hence that is the current end criteria for every simulation.


#Crash Detection with a Simple Rule-Based Algorithm

Instead of using complex AI or real-time physics, this simulation relies on a straightforward rule-based method:

1. Each new set of simulated sensor readings is added to the stack.

2. The system checks whether these readings exceed preset thresholds ( a spike in acceleration).

3. Once a crash is confirmed, an emergency alert is triggered.

In this model, overspeeding is treated as a crash since we do not yet simulate 3D environments with physical collisions.

#Emergency Alert Simulation

Upon simulated crash detection, the system:

1. Initiates alerts to emergency services, family members, or nearby drivers.

2. Sends out an SMS-style notification that includes the crash "location" on the grid, currently it shows a tab that displays information about the grid crash location and emergency status.

#Key Features

• Simulated integration of multiple sensor types for enhanced crash detection accuracy.

• Ideal for personal or student-based applications.
