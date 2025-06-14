# Rocket Simulation

## Objective

## Project Structure
rocket_simulation/
├── src/
│   ├── __init__.py           # Makes 'src' a Python package
│   ├── core/
│   │   ├── __init__.py
│   │   ├── constants.py      # Universal/Earth constants, initial rocket params
│   │   ├── atmosphere.py     # Atmospheric models (ISA, exponential, etc.)
│   │   ├── forces.py         # Functions for gravity, thrust, drag, lift
│   │   ├── rocket.py         # Rocket class (properties, mass updates, etc.)
│   │   └── simulation.py     # The main simulation loop logic
│   ├── navigation/           # (Phase 2 - for guidance, state estimation)
│   │   ├── __init__.py
│   │   ├── guidance_laws.py
│   │   ├── sensors.py
│   │   └── kalman_filter.py
│   ├── interceptor/          # (Phase 3 - for anti-missile module)
│   │   ├── __init__.py
│   │   ├── target.py
│   │   ├── tracking.py
│   │   └── intercept_logic.py
│   └── utils/
│       ├── __init__.py
│       └── plotting.py       # Functions for generating plots
│       └── units.py          # (Optional) For unit conversions if needed
├── data/
│   ├── thrust_curves/        # CSVs or other files for engine thrust profiles
│   ├── atmospheric_data/     # CSVs for ISA lookup tables if not programmatic
│   └── rocket_designs/       # YAML/JSON configs for different rocket specs
├── tests/
│   ├── __init__.py
│   ├── test_forces.py
│   ├── test_atmosphere.py
│   ├── test_simulation.py
│   └── (etc. for other modules)
├── scripts/
│   └── run_simulation.py     # Main entry point to run a simulation
├── docs/                     # Documentation (e.g., Sphinx, ReadTheDocs)
│   ├── index.rst
│   └── ...
├── .gitignore                # Files/dirs to ignore for Git (e.g., __pycache__, venv)
├── README.md                 # Project description, setup, how to run
├── requirements.txt          # Python dependencies