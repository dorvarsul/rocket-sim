import numpy as np # Needed for np.exp

def get_air_density(altitude: float, sea_level_density: float, scale_height: float) -> float:
    """
    Calculates air density using a simplified exponential model.

    Args:
        altitude (float): Current altitude above sea level (meters).
        sea_level_density (float): Air density at sea level (kg/m^3).
        scale_height (float): Atmospheric scale height (meters).

    Returns:
        float: Air density at the given altitude (kg/m^3).
    """
    if altitude < 0:
        # Air density below sea level or ground, can be set to sea_level_density
        # or 0 if you want to model vacuum below ground (less common).
        return sea_level_density
    return sea_level_density * np.exp(-altitude / scale_height)