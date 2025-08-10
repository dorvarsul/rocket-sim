import numpy as np # Needed for np.exp

def get_air_density(altitude: float, sea_level_density: float, scale_height: float) -> float:
    """
    Calculates air density using a simplified exponential model.
    """
    if altitude < 0:
        return sea_level_density
    return sea_level_density * np.exp(-altitude / scale_height)