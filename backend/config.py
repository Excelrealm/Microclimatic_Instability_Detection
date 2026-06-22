"""
Configuration settings for the atmospheric monitoring backend.
"""

# Sensor validation ranges
VALID_RANGES = {
    "temperature": (-40.0, 85.0),      # °C (BME280 spec)
    "humidity":    (0.0, 100.0),        # %
    "pressure":    (300.0, 1100.0)      # hPa
}

# Derived parameter constants
MAGNUS_A = 17.62
MAGNUS_B = 243.12

# Pressure tendency smoothing (number of readings for moving average)
PRESSURE_SMOOTHING_WINDOW = 15  # readings

# Pressure tendency classification thresholds (hPa/hr)
PRESSURE_THRESHOLDS = {
    "rising_rapidly":    1.0,
    "rising_slowly":     0.5,
    "steady_upper":      0.5,
    "steady_lower":     -0.5,
    "falling_slowly":   -0.5,
    "falling_rapidly":  -1.0
}

# Instability alert thresholds
ALERT_THRESHOLDS = {
    "small_dew_spread":     2.0,   # °C
    "high_humidity":       80.0,   # %
    "unstable_LI":         -2.0,   # °C
    "large_dew_spread":     5.0    # °C
}

# Data storage
DATA_FILE = "data/readings.json"
MAX_STORED_READINGS = 10080  # 7 days of minute-by-minute data