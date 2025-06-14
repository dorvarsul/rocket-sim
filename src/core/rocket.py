import numpy as np

class Rocket:
    """
    Represents the rocket entity within the simulation.
    Manages its physical properties (mass, dimensions) and state (position, velocity, acceleration).
    """

    def __init__(self, initial_mass, dry_mass, cross_sectional_area,
                 initial_position=np.array([0.0, 0.0, 0.0]),
                 initial_velocity=np.array([0.0, 0.0, 0.0])):
        """
        Initializes a Rocket object with its core physical characteristics and initial state.

        Args:
            initial_mass (float): The total mass of the rocket at the start of the simulation (kg).
                                  This includes the structure and all propellants.
            dry_mass (float): The mass of the rocket's structure and systems,
                              after all usable propellant has been consumed (kg).
            cross_sectional_area (float): The maximum cross-sectional area of the rocket (m^2),
                                          used for drag calculations.
            initial_position (np.ndarray): A 3-element NumPy array representing the rocket's
                                           initial position [x, y, z] in meters.
                                           Defaults to [0.0, 0.0, 0.0] (launchpad).
            initial_velocity (np.ndarray): A 3-element NumPy array representing the rocket's
                                           initial velocity [vx, vy, vz] in m/s.
                                           Defaults to [0.0, 0.0, 0.0] (at rest).
        """
        if not isinstance(initial_position, np.ndarray) or initial_position.shape != (3,):
            raise ValueError("initial_position must be a 3-element NumPy array.")
        if not isinstance(initial_velocity, np.ndarray) or initial_velocity.shape != (3,):
            raise ValueError("initial_velocity must be a 3-element NumPy array.")

        self.mass = float(initial_mass)
        self.dry_mass = float(dry_mass)
        self.cross_sectional_area = float(cross_sectional_area)

        # Current state vectors
        self.position = initial_position.astype(float)
        self.velocity = initial_velocity.astype(float)
        self.acceleration = np.array([0.0, 0.0, 0.0], dtype=float) # Initial acceleration is zero

        # Propellant management
        self.propellant_mass_initial = self.mass - self.dry_mass
        if self.propellant_mass_initial < 0:
            # This should ideally be caught by input validation in a more robust system
            print("Warning: Initial mass is less than dry mass. Adjusting propellant to 0.")
            self.propellant_mass_initial = 0.0
            self.mass = self.dry_mass # Adjust total mass to dry mass
        self.current_propellant_mass = self.propellant_mass_initial

        # Additional properties for tracking/logging
        self._previous_altitude = self.altitude # Used for impact detection

    def update_state(self, dt, total_force, mass_flow_rate=0.0):
        """
        Updates the rocket's position, velocity, acceleration, and mass
        based on the net forces acting on it and the time step.

        Args:
            dt (float): The time step for the simulation (seconds).
            total_force (np.ndarray): A 3-element NumPy array representing the
                                      net force vector [Fx, Fy, Fz] acting on the rocket (N).
            mass_flow_rate (float, optional): The rate at which propellant mass is
                                              consumed (kg/s). Defaults to 0.0.
        """
        # 1. Update Acceleration (Newton's Second Law: F = ma => a = F/m)
        self.acceleration = total_force / self.mass

        # 2. Update Velocity (Euler integration: v_new = v_old + a * dt)
        self.velocity += self.acceleration * dt

        # 3. Update Position (Euler integration: p_new = p_old + v_new * dt)
        # Using the *new* velocity (semi-implicit Euler) generally gives better stability
        self.position += self.velocity * dt

        # 4. Update Mass (if engine is burning)
        if mass_flow_rate > 0 and self.current_propellant_mass > 0:
            mass_consumed = mass_flow_rate * dt
            # Ensure we don't consume more propellant than is available
            if mass_consumed > self.current_propellant_mass:
                mass_consumed = self.current_propellant_mass # Consume remaining
                self.current_propellant_mass = 0.0
            else:
                self.current_propellant_mass -= mass_consumed
            
            self.mass -= mass_consumed
            # Ensure total mass doesn't drop below the dry mass
            if self.mass < self.dry_mass:
                self.mass = self.dry_mass # Clamp at dry mass
        
        # Update previous altitude for future impact checks (optional, but useful)
        self._previous_altitude = self.altitude

    @property
    def altitude(self):
        """
        Returns the current altitude of the rocket (z-component of position).
        Assumes Z is the vertical axis.
        """
        return self.position[2]

    @property
    def speed(self):
        """
        Returns the current scalar speed (magnitude of velocity) of the rocket.
        """
        return np.linalg.norm(self.velocity)

    @property
    def has_propellant(self):
        """
        Returns True if the rocket still has usable propellant, False otherwise.
        """
        return self.current_propellant_mass > 0

# Example of how you might instantiate and use it (for testing, not part of the class itself)
if __name__ == "__main__":
    # This block only runs if rocket.py is executed directly
    print("Running a quick test of the Rocket class:")
    test_rocket = Rocket(
        initial_mass=100.0,
        dry_mass=10.0,
        cross_sectional_area=0.5,
        initial_position=np.array([0.0, 0.0, 100.0]), # 100m altitude
        initial_velocity=np.array([0.0, 0.0, 0.0])
    )

    print(f"Initial Mass: {test_rocket.mass} kg")
    print(f"Initial Altitude: {test_rocket.altitude} m")
    print(f"Initial Speed: {test_rocket.speed} m/s")
    print(f"Has Propellant: {test_rocket.has_propellant}")

    # Simulate a small time step with some force and mass flow
    test_force = np.array([0.0, 0.0, 1500.0]) # 1500N upwards thrust
    dt = 0.1
    mass_flow_rate_test = 5.0 # kg/s

    test_rocket.update_state(dt, test_force, mass_flow_rate_test)

    print(f"\nAfter {dt}s:")
    print(f"New Mass: {test_rocket.mass:.2f} kg")
    print(f"New Altitude: {test_rocket.altitude:.2f} m")
    print(f"New Speed: {test_rocket.speed:.2f} m/s")
    print(f"New Velocity: {test_rocket.velocity}")
    print(f"New Acceleration: {test_rocket.acceleration}")
    print(f"Has Propellant: {test_rocket.has_propellant}")

    # Burn all propellant quickly for demonstration
    test_rocket.mass = test_rocket.dry_mass + 1.0 # Set just above dry mass
    test_rocket.current_propellant_mass = 1.0

    print("\nBurning remaining propellant...")
    for _ in range(5): # Simulate 5 more steps
        test_rocket.update_state(dt, test_force, mass_flow_rate_test)
        print(f"  Mass: {test_rocket.mass:.2f}, Propellant: {test_rocket.current_propellant_mass:.2f}")

    print(f"Has Propellant after burn: {test_rocket.has_propellant}")
    print(f"Final Mass: {test_rocket.mass:.2f} (should be dry mass)")