"""
Input validation and sensor data quality checks.
"""

from config import VALID_RANGES


def validate_sensor_data(temperature: float, humidity: float, pressure: float) -> tuple[bool, str]:
    """
    Validate incoming sensor data against expected ranges.
    
    Returns:
        (is_valid, error_message)
    """
    # Check for missing values
    if temperature is None or humidity is None or pressure is None:
        return False, "Missing sensor values"

    # Check temperature range
    t_min, t_max = VALID_RANGES["temperature"]
    if not (t_min <= temperature <= t_max):
        return False, f"Temperature {temperature}°C out of valid range ({t_min} to {t_max}°C)"

    # Check humidity range
    h_min, h_max = VALID_RANGES["humidity"]
    if not (h_min <= humidity <= h_max):
        return False, f"Humidity {humidity}% out of valid range ({h_min} to {h_max}%)"

    # Check pressure range
    p_min, p_max = VALID_RANGES["pressure"]
    if not (p_min <= pressure <= p_max):
        return False, f"Pressure {pressure}hPa out of valid range ({p_min} to {p_max}hPa)"

    return True, "Valid"