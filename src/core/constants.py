# src/core/constants.py

import numpy as np

# --- Universal Constants ---
# Gravitational constant (m^3 kg^-1 s^-2)
G = 6.67430e-11

# --- Earth Parameters --
G0 = 9.80665 

# --- Atmospheric Model Parameters (for a simplified exponential model) ---
ATM_SEA_LEVEL_DENSITY = 1.225
ATM_SCALE_HEIGHT = 8500.0

# --- Simulation Control Parameters ---
TIME_STEP = 0.1
SIMULATION_DURATION = 600.0 # (In Seconds)
ROCKET_CONFIG_FILENAME = "small_rocket.yaml"