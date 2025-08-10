import numpy as np

class Rocket:
    """
    Represents the rocket entity within the simulation.
    Manages its physical properties (mass, dimensions) and state (position, velocity, acceleration).
    """

    def __init__(self, initial_mass, dry_mass, cross_sectional_area,
                 initial_position=np.array([0.0, 0.0, 0.0]),
                 initial_velocity=np.array([0.0, 0.0, 0.0])):
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
            print("Warning: Initial mass is less than dry mass. Adjusting propellant to 0.")
            self.propellant_mass_initial = 0.0
            self.mass = self.dry_mass # Adjust total mass to dry mass
        self.current_propellant_mass = self.propellant_mass_initial

        # Additional properties for tracking/logging
        self._previous_altitude = self.altitude # Used for impact detection

    def update_state(self, dt, total_force, mass_flow_rate=0.0):
        self.acceleration = total_force / self.mass
        self.velocity += self.acceleration * dt
        self.position += self.velocity * dt

        if mass_flow_rate > 0 and self.current_propellant_mass > 0:
            mass_consumed = mass_flow_rate * dt

            if mass_consumed > self.current_propellant_mass:
                mass_consumed = self.current_propellant_mass
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
        return self.position[2]

    @property
    def speed(self):
        return np.linalg.norm(self.velocity)

    @property
    def has_propellant(self):
        return self.current_propellant_mass > 0

if __name__ == "__main__":
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