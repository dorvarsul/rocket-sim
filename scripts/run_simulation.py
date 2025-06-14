import numpy as np
import yaml
import os

import matplotlib.pyplot as plt
import pandas as pd

# Import constants and classes from your src directory
from src.core import constants
from src.core.rocket import Rocket
from src.core.atmosphere import get_air_density

# Which rocket config file will this simulation load?
ROCKET_CONFIG = "small_rocket.yaml"

def load_rocket_config(config_filepath: str) -> dict | None:
    """Loads rocket parameters from a YAML configuration file."""
    try:
        with open(config_filepath, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Error: Rocket config file not found at {config_filepath}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML config file: {e}")
        return None

def run_simulation(rocket_config_name: str = ROCKET_CONFIG):
    """
    Runs the rocket simulation using parameters loaded from a config file.

    Args:
        rocket_config_name (str): The filename of the rocket configuration
                                  (e.g., "example_rocket.yaml").
    """
    current_dir = os.path.dirname(__file__)
    config_filepath = os.path.join(current_dir, '..', 'data', 'rocket_designs', rocket_config_name)
    config_filepath = os.path.abspath(config_filepath)

    rocket_data = load_rocket_config(config_filepath)
    if not rocket_data:
        print("Failed to load rocket configuration. Exiting simulation.")
        return None, None, None, None, None, None

    # Extract parameters from the loaded configuration
    initial_mass = rocket_data['mass']['initial']
    dry_mass = rocket_data['mass']['dry']
    engine_thrust = rocket_data['engine']['thrust_N']
    engine_burn_time = rocket_data['engine']['burn_time_s']
    drag_coefficient = rocket_data['aerodynamics']['drag_coefficient']
    cross_sectional_area = rocket_data['aerodynamics']['cross_sectional_area_m2']

    # Calculate propellant mass and mass flow rate
    propellant_mass = initial_mass - dry_mass
    engine_mass_flow_rate = propellant_mass / engine_burn_time if engine_burn_time > 0 else 0.0

    # --- CORRECTED LINES BELOW ---
    # Default initial state if not provided in YAML config
    default_initial_position = np.array([0.0, 0.0, 0.0])
    default_initial_velocity = np.array([0.0, 0.0, 0.0])

    # Get initial position from config, or use default
    initial_pos = np.array(rocket_data.get('initial_state', {}).get('position_m', default_initial_position.tolist()))
    # Get initial velocity from config, or use default
    initial_vel = np.array(rocket_data.get('initial_state', {}).get('velocity_ms', default_initial_velocity.tolist()))
    # --- END CORRECTED LINES ---

    # Initialize Rocket object
    rocket = Rocket(
        initial_mass=initial_mass,
        dry_mass=dry_mass,
        cross_sectional_area=cross_sectional_area,
        initial_position=initial_pos,
        initial_velocity=initial_vel
    )

    # Simulation loop setup
    current_time = 0.0
    times = [current_time]
    positions = [rocket.position.copy()]
    velocities = [rocket.velocity.copy()]
    masses = [rocket.mass]
    altitudes = [rocket.altitude]
    speeds = [rocket.speed]


    # Simulation loop
    while current_time < constants.SIMULATION_DURATION and rocket.altitude >= 0:
        # 1. Calculate Forces
        thrust_force = np.array([0.0, 0.0, engine_thrust]) if current_time <= engine_burn_time else np.array([0.0, 0.0, 0.0])
        gravity_force = np.array([0.0, 0.0, -rocket.mass * constants.G0])

        current_air_density = get_air_density(rocket.altitude,
                                            constants.ATM_SEA_LEVEL_DENSITY,
                                            constants.ATM_SCALE_HEIGHT)
        
        drag_magnitude = 0.0
        if rocket.speed > 1e-6: # Avoid division by near-zero speed. Use a small epsilon.
            drag_magnitude = 0.5 * current_air_density * rocket.speed**2 * drag_coefficient * cross_sectional_area
        
        drag_force = -rocket.velocity / rocket.speed * drag_magnitude if rocket.speed > 1e-6 else np.array([0.0, 0.0, 0.0])

        total_force = thrust_force + gravity_force + drag_force

        # 2. Update Rocket State (position, velocity, mass)
        current_mass_flow_rate = engine_mass_flow_rate if current_time <= engine_burn_time else 0.0
        rocket.update_state(constants.TIME_STEP, total_force, current_mass_flow_rate)

        # 3. Increment Time
        current_time += constants.TIME_STEP

        # 4. Store data
        times.append(current_time)
        positions.append(rocket.position.copy())
        velocities.append(rocket.velocity.copy())
        masses.append(rocket.mass)
        altitudes.append(rocket.altitude)
        speeds.append(rocket.speed)

        # 5. Check termination conditions
        if rocket.altitude <= 0 and rocket.velocity[2] < 0:
            print(f"Impact at t={current_time:.2f}s, altitude={rocket.altitude:.2f}m")
            break

    return np.array(times), np.array(positions), np.array(velocities), np.array(masses), np.array(altitudes), np.array(speeds)

if __name__ == "__main__":
    rocket_config_filename = ROCKET_CONFIG

    try:
        import numpy as np
        import matplotlib.pyplot as plt
        import pandas as pd
        import yaml
    except ImportError:
        print("Required libraries not found. Please run: pip install numpy matplotlib pandas pyyaml")
        exit()

    times, positions, velocities, masses, altitudes, speeds = run_simulation(rocket_config_filename)

    if times is not None:
        df = pd.DataFrame({
            'time': times,
            'x': positions[:, 0],
            'y': positions[:, 1],
            'z': positions[:, 2],
            'vx': velocities[:, 0],
            'vy': velocities[:, 1],
            'vz': velocities[:, 2],
            'mass': masses,
            'speed': speeds
        })

        plt.figure(figsize=(12, 10))

        plt.subplot(4, 1, 1)
        plt.plot(df['time'], df['z'])
        plt.title(f'Altitude vs. Time ({rocket_config_filename.split(".")[0]})')
        plt.xlabel('Time (s)')
        plt.ylabel('Altitude (m)')
        plt.grid(True)

        plt.subplot(4, 1, 2)
        plt.plot(df['time'], df['speed'])
        plt.title('Speed vs. Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Speed (m/s)')
        plt.grid(True)

        plt.subplot(4, 1, 3)
        plt.plot(df['time'], df['mass'])
        plt.title('Mass vs. Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Mass (kg)')
        plt.grid(True)
        
        plt.subplot(4, 1, 4)
        plt.plot(df['time'], df['vz'])
        plt.title('Vertical Velocity vs. Time')
        plt.xlabel('Time (s)')
        plt.ylabel('Vertical Velocity (m/s)')
        plt.grid(True)

        plt.tight_layout()
        plt.show()

        print(f"\nSimulation Complete for {rocket_config_filename.split('.')[0]}:")
        print(f"Max Altitude: {df['z'].max():.2f} m")
        print(f"Max Speed: {df['speed'].max():.2f} m/s")
        idx_max_alt = np.argmax(df['z'])
        print(f"Time at Max Altitude: {df['time'][idx_max_alt]:.2f} s")