"""
Rocket Simulation Script

This script provides the main entry point for running a basic rocket simulation.
It loads rocket parameters from a YAML configuration file, simulates its trajectory
under the influence of thrust, gravity, and atmospheric drag using a numerical
integration method, and then visualizes the results through 2D and 3D plots.
"""

import numpy as np
import yaml # For loading rocket configuration from YAML files
import os   # For path manipulation, ensuring configurations are found reliably

import matplotlib.pyplot as plt # For creating various plots
from mpl_toolkits.mplot3d import Axes3D # Specifically for 3D trajectory plotting
import pandas as pd # For convenient data handling and structuring simulation results

# Import core simulation components from the 'src' directory
from src.core import constants          # Contains universal physical constants and simulation parameters
from src.core.rocket import Rocket      # Defines the Rocket class, managing its physical state
from src.core.atmosphere import get_air_density # Function to calculate air density at a given altitude

def load_rocket_config(config_filepath: str) -> dict | None:
    """
    Loads rocket parameters from a YAML configuration file.
    """
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

def run_simulation(rocket_config_name: str = "example_rocket.yaml"):
    """
    Executes the rocket trajectory simulation using parameters from a specified config file.
    """

    # Load the YAML file
    current_dir = os.path.dirname(__file__)
    config_filepath = os.path.join(current_dir, '..', 'data', 'rocket_designs', rocket_config_name)
    config_filepath = os.path.abspath(config_filepath)

    # Attempt to load the rocket's configuration data
    rocket_data = load_rocket_config(config_filepath)
    if not rocket_data:
        print("Failed to load rocket configuration. Exiting simulation.")
        return None, None, None, None, None, None

    # --- Extract simulation parameters from the loaded configuration ---
    # Rocket mass properties
    initial_mass = rocket_data['mass']['initial']
    dry_mass = rocket_data['mass']['dry']

    # Engine performance parameters
    engine_thrust = rocket_data['engine']['thrust_N']
    engine_burn_time = rocket_data['engine']['burn_time_s']

    # Aerodynamic properties
    drag_coefficient = rocket_data['aerodynamics']['drag_coefficient']
    cross_sectional_area = rocket_data['aerodynamics']['cross_sectional_area_m2']

    # Calculate propellant mass and mass flow rate
    propellant_mass = initial_mass - dry_mass
    engine_mass_flow_rate = propellant_mass / engine_burn_time if engine_burn_time > 0 else 0.0

    # --- Set up Initial State of the Rocket (Default parameters) ---
    default_initial_position = np.array([0.0, 0.0, 0.0]) # Default start at origin [x, y, z]
    default_initial_velocity = np.array([0.0, 0.0, 0.0]) # Default start from rest [vx, vy, vz]
    default_initial_direction = np.array([0.0, 0.0, 1.0]) # Default thrust direction: straight up

    # Retrieve actual initial position from config, or use default
    initial_pos = np.array(rocket_data.get('initial_state', {}).get('position_m', default_initial_position.tolist()))
    # Retrieve actual initial velocity from config, or use default (used if rocket starts with pre-existing speed)
    initial_vel = np.array(rocket_data.get('initial_state', {}).get('velocity_ms', default_initial_velocity.tolist()))
    # Retrieve initial thrust direction from config
    initial_thrust_direction = np.array(rocket_data.get('initial_state', {}).get('initial_direction_vector', default_initial_direction.tolist()))
    
    dir_magnitude = np.linalg.norm(initial_thrust_direction)

    if dir_magnitude > 1e-9: # To avoid dividing by Zero
        initial_thrust_direction = initial_thrust_direction / dir_magnitude
    else:
        initial_thrust_direction = default_initial_direction
        print("Warning: Initial direction vector was invalid (zero or near-zero), defaulting to [0,0,1] (vertical).")

    # --- NEW: Pre-flight Check: Thrust-to-Weight Ratio ---
    initial_weight = initial_mass * constants.G0

    # Calculate the effective vertical component of the initial thrust.
    # Only the Z-component of the thrust direction contributes to directly opposing gravity.
    effective_vertical_thrust = engine_thrust * initial_thrust_direction[2]

    # Check if the effective vertical thrust is sufficient to overcome gravity.
    # If it's less than the initial weight, the rocket will not lift off.
    if effective_vertical_thrust < initial_weight:
        # Calculate the initial Thrust-to-Weight Ratio (TWR) for vertical component
        initial_twr = effective_vertical_thrust / initial_weight
        print(f"\n--- WARNING: Insufficient Thrust for Lift-off ---")
        print(f"Rocket '{rocket_config_name.split('.')[0]}' may not lift off the ground due to low effective vertical thrust.")
        print(f"  Initial Mass: {initial_mass:.2f} kg")
        print(f"  Initial Weight (Gravity Force): {initial_weight:.2f} N")
        print(f"  Total Engine Thrust: {engine_thrust:.2f} N")
        print(f"  Initial Direction Vector (Normalized): {np.round(initial_thrust_direction, 3)}") # Round for cleaner output
        print(f"  Effective Vertical Thrust (Thrust * Z-component of direction): {effective_vertical_thrust:.2f} N")
        print(f"  Initial Thrust-to-Weight Ratio (Vertical component): {initial_twr:.3f} (must be > 1 for lift-off)")
        print(f"  Consider increasing 'engine_thrust' or adjusting 'initial_direction_vector' for a steeper angle (larger Z component).")
        print(f"--------------------------------------------------\n")
    else:
        # If thrust is sufficient, print a confirmation message with the TWR.
        initial_twr = effective_vertical_thrust / initial_weight
        print(f"\n--- Pre-flight Check: Thrust Sufficient for Lift-off ---")
        print(f"  Rocket '{rocket_config_name.split('.')[0]}' has sufficient vertical thrust for lift-off.")
        print(f"  Initial Thrust-to-Weight Ratio (Vertical component): {initial_twr:.3f}")
        print(f"--------------------------------------------------\n")

    # Initialize Rocket object with its starting parameters
    rocket = Rocket(
        initial_mass=initial_mass,
        dry_mass=dry_mass,
        cross_sectional_area=cross_sectional_area,
        initial_position=initial_pos,
        initial_velocity=initial_vel
    )

    # --- Data Storage for Simulation Results ---
    current_time = 0.0
    times = [current_time]
    positions = [rocket.position.copy()]
    velocities = [rocket.velocity.copy()]
    masses = [rocket.mass]
    altitudes = [rocket.altitude]
    speeds = [rocket.speed]


    # --- Main Simulation Loop ---
    while current_time < constants.SIMULATION_DURATION and rocket.altitude >= -1.0:
        if current_time <= engine_burn_time:
            thrust_force = initial_thrust_direction * engine_thrust
        else:
            thrust_force = np.array([0.0, 0.0, 0.0]) # No thrust after engine cutoff
        
        gravity_force = np.array([0.0, 0.0, -rocket.mass * constants.G0])

        # Drag Force: Opposes the rocket's current direction of motion.
        current_air_density = get_air_density(rocket.altitude,
                                            constants.ATM_SEA_LEVEL_DENSITY,
                                            constants.ATM_SCALE_HEIGHT)
        
        drag_magnitude = 0.0
        # Calculate drag magnitude only if the rocket is moving to avoid division by zero
        if rocket.speed > 1e-6: # Check for non-zero (or near-zero) speed
            drag_magnitude = 0.5 * current_air_density * rocket.speed**2 * drag_coefficient * cross_sectional_area
        
        # Calculate drag force vector: direction opposite to velocity, magnitude calculated above.
        drag_force = -rocket.velocity / rocket.speed * drag_magnitude if rocket.speed > 1e-6 else np.array([0.0, 0.0, 0.0])

        # Sum all individual forces to get the total net force acting on the rocket
        total_force = thrust_force + gravity_force + drag_force

        # 2. Update Rocket State (position, velocity, and mass)
        # Determine the current mass flow rate for updating the rocket's mass.
        current_mass_flow_rate = engine_mass_flow_rate if current_time <= engine_burn_time else 0.0
        # Call the rocket's method to update its state based on net force and mass loss over the time step.
        rocket.update_state(constants.TIME_STEP, total_force, current_mass_flow_rate)

        # 3. Advance Simulation Time for the next iteration
        current_time += constants.TIME_STEP

        # 4. Store the rocket's updated state data
        times.append(current_time)
        positions.append(rocket.position.copy())
        velocities.append(rocket.velocity.copy())
        masses.append(rocket.mass)
        altitudes.append(rocket.altitude)
        speeds.append(rocket.speed)

        # 5. Check for a termination condition: Rocket impacts the ground while descending.
        # This prevents the simulation from continuing infinitely below ground level.
        if rocket.altitude <= 0 and rocket.velocity[2] < 0:
            print(f"Impact detected at t={current_time:.2f}s, final altitude={rocket.altitude:.2f}m")
            break # Exit the simulation loop upon impact

    # Convert lists of simulation data to NumPy arrays before returning.
    # NumPy arrays are more efficient for numerical operations and plotting.
    return np.array(times), np.array(positions), np.array(velocities), \
           np.array(masses), np.array(altitudes), np.array(speeds)

if __name__ == "__main__":
    # --- Main Execution Block ---
    # This block of code runs only when the script is executed directly (not when imported as a module).
    rocket_config_filename = constants.ROCKET_CONFIG_FILENAME

    # --- Dependency Check ---
    try:
        import numpy as np
        import matplotlib.pyplot as plt
        import pandas as pd
        import yaml
        from mpl_toolkits.mplot3d import Axes3D # Specifically check for 3D plotting tools
    except ImportError:
        print("One or more required Python libraries are not found.")
        print("Please install them using: pip install numpy matplotlib pandas pyyaml")
        exit() # Terminate script execution

    # --- Run the Simulation ---
    # Call the main simulation function to get all the trajectory data.
    times, positions, velocities, masses, altitudes, speeds = run_simulation(rocket_config_filename)

    # Proceed with plotting and analysis only if the simulation ran successfully
    if times is not None:
        # Convert the collected raw simulation data into a Pandas DataFrame.
        df = pd.DataFrame({
            'time': times,          # Simulation time
            'x': positions[:, 0],   # X-coordinate of position
            'y': positions[:, 1],   # Y-coordinate of position
            'z': positions[:, 2],   # Z-coordinate (Altitude) of position
            'vx': velocities[:, 0], # X-component of velocity
            'vy': velocities[:, 1], # Y-component of velocity
            'vz': velocities[:, 2], # Z-component (Vertical) of velocity
            'mass': masses,         # Rocket mass over time
            'speed': speeds         # Total speed of the rocket
        })

        # --- Combined Plotting Section ---
        # Create a single Matplotlib figure to display all the plots together.
        fig = plt.figure(figsize=(15, 12)) 
        gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 1.5]) 

        # Plot 1: Altitude vs. Time (converted to Kilometers)
        ax1 = fig.add_subplot(gs[0, 0]) # Placed in the first row, first column
        ax1.plot(df['time'], df['z'] / 1000, color='blue') # Convert meters to kilometers
        ax1.set_title(f'Altitude vs. Time ({rocket_config_filename.split(".")[0]})')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Altitude (km)')
        ax1.grid(True) # Add a grid for easier reading of values

        # Plot 2: Speed vs. Time
        ax2 = fig.add_subplot(gs[0, 1]) # Placed in the first row, second column
        ax2.plot(df['time'], df['speed'], color='green')
        ax2.set_title('Speed vs. Time')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Speed (m/s)')
        ax2.grid(True)

        # Plot 3: Mass vs. Time (demonstrating propellant depletion)
        ax3 = fig.add_subplot(gs[1, 0]) # Placed in the second row, first column
        ax3.plot(df['time'], df['mass'], color='red')
        ax3.set_title('Mass vs. Time')
        ax3.set_xlabel('Time (s)')
        ax3.set_ylabel('Mass (kg)')
        ax3.grid(True)
        
        # Plot 4: Vertical Velocity vs. Time (showing ascent, max velocity, and descent)
        ax4 = fig.add_subplot(gs[1, 1]) # Placed in the second row, second column
        ax4.plot(df['time'], df['vz'], color='orange')
        ax4.set_title('Vertical Velocity vs. Time')
        ax4.set_xlabel('Time (s)')
        ax4.set_ylabel('Vertical Velocity (m/s)')
        ax4.grid(True)

        # Plot 5: 3D Trajectory Plot
        ax5 = fig.add_subplot(gs[2, :], projection='3d') 
        ax5.plot(df['x'], df['y'], df['z'] / 1000, label='Rocket Trajectory', color='purple')
        ax5.set_xlabel('X Position (m)')
        ax5.set_ylabel('Y Position (m)')
        ax5.set_zlabel('Altitude (km)') # Z-axis label in kilometers
        ax5.set_title(f'Rocket Trajectory 3D Plot ({rocket_config_filename.split(".")[0]})')
        ax5.grid(True)
        
        ax5.scatter([0], [0], [0], color='red', marker='o', s=100, label='Launch Site (0,0,0)', alpha=0.7)
        # Mark the final position of the rocket (e.g., impact point) with a blue triangle.
        ax5.scatter([df['x'].iloc[-1]], [df['y'].iloc[-1]], [df['z'].iloc[-1]/1000],
                    color='blue', marker='^', s=100, label='Final Position', alpha=0.7)
        ax5.legend() # Display the legend for the markers and trajectory line

        plt.tight_layout() # Automatically adjust subplot parameters for a tight layout, preventing overlaps
        plt.show() # Display the single figure containing all plots

        # --- Console Output of Key Simulation Metrics ---
        print(f"\n--- Simulation Results for {rocket_config_filename.split('.')[0]} ---")
        print(f"Max Altitude: {df['z'].max():.2f} m ({df['z'].max()/1000:.2f} km)")
        print(f"Max Speed: {df['speed'].max():.2f} m/s")
        # Find the time at which the rocket reached its maximum altitude
        idx_max_alt = np.argmax(df['z'])
        print(f"Time at Max Altitude: {df['time'][idx_max_alt]:.2f} s")
        print(f"Final Position (X, Y, Z): ({df['x'].iloc[-1]:.2f} m, {df['y'].iloc[-1]:.2f} m, {df['z'].iloc[-1]:.2f} m)")
        print(f"Final Velocity (Vx, Vy, Vz): ({df['vx'].iloc[-1]:.2f} m/s, {df['vy'].iloc[-1]:.2f} m/s, {df['vz'].iloc[-1]:.2f} m/s)")