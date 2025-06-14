import numpy as np

# --- Universal Constants ---
# Gravitational constant (m^3 kg^-1 s^-2)
G = 6.67430e-11

# --- Earth Parameters ---
# Mass of Earth (kg)
M_EARTH = 5.972e24
# Mean Radius of Earth (m) - used for calculating distance from center of Earth
R_EARTH = 6.371e6
# Standard acceleration due to gravity at sea level (m/s^2)
G0 = 9.80665 # Often used as a standard value

# --- Atmospheric Model Parameters (for a simplified exponential model) ---
# Sea level air density (kg/m^3)
ATM_SEA_LEVEL_DENSITY = 1.225
# Scale height (m) - approximate, varies with temperature and atmospheric conditions
ATM_SCALE_HEIGHT = 8500.0

# --- Simulation Control Parameters ---
# Time step for numerical integration (seconds)
TIME_STEP = 0.1
# Maximum duration of the simulation (seconds)
SIMULATION_DURATION = 600.0 # e.g., 10 minutes to see ascent and descent