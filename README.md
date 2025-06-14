# Rocket Trajectory Simulation

---

This project provides a Python-based simulation environment for modeling a rocket's trajectory under various physical forces. It's designed to be easily configured using **YAML files**, letting you quickly define and test different rocket designs and initial conditions. The simulation calculates the rocket's path through the atmosphere and visualizes the results with 2D performance graphs and a 3D trajectory plot.

## ✨ Features

* **Configurable Rocket Design:** Define rocket properties (mass, engine thrust, burn time, aerodynamics) and initial conditions using intuitive YAML configuration files.
* **Physics-Based Simulation:** Models key forces acting on a rocket:
    * **Thrust:** Applied based on engine parameters and a user-defined initial direction vector.
    * **Gravity:** Constant gravitational acceleration pulling downwards.
    * **Aerodynamic Drag:** Calculated based on current speed, atmospheric density (using an exponential model), rocket cross-sectional area, and a drag coefficient.
* **Numerical Integration:** Uses a time-stepping approach (Euler's method) to update the rocket's position, velocity, and mass over time.
* **Visualizations:** Generates comprehensive plots after each simulation run:
    * Altitude vs. Time
    * Speed vs. Time
    * Mass vs. Time
    * Vertical Velocity vs. Time
    * Interactive 3D Trajectory Plot
* **Pre-flight Checks:** Includes a helpful check to warn you if your rocket's initial vertical thrust is insufficient to overcome gravity, preventing immediate ground impact.
* **Modular Design:** Separates core physics calculations (`src/core`) from the main simulation script (`scripts/`).

---

## 📂 Project Structure

Understanding the project's layout helps you navigate and modify the code effectively.
### Folder and File Breakdown:

* **`rocket_simulation/`**
    * This is the **root directory** of your project. All other folders and files reside within it.

* **`data/`**
    * This folder stores static data files used by the simulation.
    * **`rocket_designs/`**: Contains various **YAML (`.yaml`) files**, each defining the specific physical parameters (like mass, engine thrust, aerodynamics) and initial conditions for different rocket models you want to simulate. `example_rocket.yaml` is provided as a template.

* **`scripts/`**
    * Houses the main **executable Python scripts** that drive the simulation process.
    * **`run_simulation.py`**: This is the primary script you'll run. It's responsible for loading the rocket configuration, initiating the simulation, performing calculations, and generating the visualization plots.

* **`src/`**
    * Contains the **core source code** of the simulation, organized into modules for reusability and clarity.
    * **`core/`**: This sub-folder holds the fundamental building blocks of the simulation's physics and logic:
        * **`atmosphere.py`**: Defines functions related to the **atmospheric model**, primarily for calculating air density at different altitudes.
        * **`constants.py`**: Stores **universal physical constants** (like gravity, atmospheric properties) and global simulation settings (e.g., time step, simulation duration). It also specifies which rocket configuration file to load by default.
        * **`rocket.py`**: Defines the `Rocket` class, which encapsulates the rocket's physical properties (mass, cross-sectional area) and its dynamic state (position, velocity). It includes methods to update the rocket's state based on applied forces.

* **`.gitignore`**
    * A critical file for Git. It tells Git which files and directories to **ignore** and not track in your repository. This typically includes virtual environments (`venv/`), compiled Python files (`__pycache__/`, `.pyc`), and IDE-specific configuration files.

* **`README.md`**
    * This file! It serves as the project's main documentation, providing an overview, setup instructions, usage guidelines, and more.

* **`venv/`**
    * This directory is created when you set up a **Python virtual environment**. It isolates the project's specific Python dependencies from your system's global Python installation. It should always be listed in `.gitignore`.

* **`requirements.txt`**
    * This file lists all the Python libraries and their versions that your project depends on. It allows others to easily recreate your exact development environment using `pip install -r requirements.txt`.

---

## 🚀 Getting Started

Follow these steps to set up and run the rocket simulation on your local machine.

### Prerequisites

* **Python 3.8+:** Download and install Python from [python.org](https://www.python.org/).
* **Git:** Install Git from [git-scm.com](https://git-scm.com/).

### Installation

**Clone the repository:**
    ```bash
    git clone [https://github.com/dorvarsul/rocket_simulation.git](https://github.com/your-username/rocket_simulation.git)
    cd rocket_simulation
    ```

---

## 🚀 Usage

To run a simulation, simply execute the `run_simulation.py` script:

1.  **Activate your virtual environment** (if you haven't already).
2.  **Run the script from the project root:**
    ```bash
    python scripts/run_simulation.py
    ```
    The script will load the rocket design specified in `src/core/constants.py` (by default, `example_rocket.yaml`), run the simulation, display console output, and pop up the plots.

### Customizing Rocket Designs

You can easily define your own rocket designs:

1.  Create a new YAML file (e.g., `my_custom_rocket.yaml`) inside the `data/rocket_designs/` directory.
2.  Follow the structure of `example_rocket.yaml` to define your rocket's `mass`, `engine`, `aerodynamics`, and `initial_state`.
3.  Open `src/core/constants.py` and change the `ROCKET_CONFIG_FILENAME` constant to your new filename:
    ```python
    # src/core/constants.py
    # ...
    ROCKET_CONFIG_FILENAME = "my_custom_rocket.yaml" # Change this line
    # ...
    ```
4.  Run the simulation script as described above.

---

## ⚙️ Configuration Details

* **`data/rocket_designs/`**: Contains YAML files defining different rocket configurations.
* **`src/core/constants.py`**: Stores global simulation parameters (like `TIME_STEP`, `SIMULATION_DURATION`, gravitational constant `G0`, atmospheric model parameters, and the name of the active rocket configuration file). You can adjust these values to control the simulation's precision and environment.
* **`src/core/rocket.py`**: Defines the `Rocket` class, which manages the rocket's physical state (mass, position, velocity, etc.) and provides methods for updating it based on applied forces.
* **`src/core/atmosphere.py`**: Contains the `get_air_density` function, which models how air density changes with altitude.

---

## 📐 Simulation Model Notes

The current simulation uses simplified models for clarity and computational efficiency:

* **Constant Gravity:** Assumes a constant gravitational acceleration (`G0`) regardless of altitude.
* **Fixed Thrust Direction:** The direction of thrust is constant throughout the engine burn, as defined in `initial_direction_vector`.
* **Simplified Atmosphere:** Uses a basic exponential model for atmospheric density.
* **Euler Integration:** A basic numerical method is used for integrating forces to update velocity and position. While simple, it can accumulate errors over long simulations. For more advanced simulations, consider higher-order integration methods (e.g., Runge-Kutta).

Feel free to explore and modify these core components in the `src/core` directory to experiment with more complex or accurate physical models!