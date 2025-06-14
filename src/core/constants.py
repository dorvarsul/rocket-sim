import numpy as np

# --- Universal Constants ---
G = 6.67430e-11 # Gravitational Constant (m^3 kg^-1 s^-2)

# --- Earth Parameters ---
M_EARTH = 5.972e24 # Mass of Earth (kg)
R_EARTH = 6.371e6 # Mean Radius of Earth (m)
G0 = 9.80665 # Standard acceleration due to gravity at sea level (m/s^2)

# --- Atmospheric Model Parameters (simplified exponential model) ---
ATM_SEA_LEVEL_DENSITY = 1.225 # Sea Level air density (kg/m^3)
ATM_SCALE_HEIGHT = 8500.0 # Scale Height (m) - approximate, varies with temperature and atmospheric conditions

# --- Simulation Control Parameters ---
TIME_STEP = 0.1
SIMULATION_DURATION = 600.0 # Duration of Simulation in seconds