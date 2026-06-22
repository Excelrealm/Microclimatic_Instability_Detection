"""
Atmospheric data processing: dew point, instability indices, and alerts.
"""

import math
import numpy as np
from typing import Optional

from config import (
    MAGNUS_A, MAGNUS_B,
    PRESSURE_THRESHOLDS,
    ALERT_THRESHOLDS
)


def calculate_dew_point(temperature: float, humidity: float) -> float:
    """Calculate dew point temperature using the Magnus-Tetens formula."""
    a = MAGNUS_A
    b = MAGNUS_B
    alpha = math.log(humidity / 100.0) + (a * temperature) / (b + temperature)
    dew_point = (b * alpha) / (a - alpha)
    return round(dew_point, 2)


def calculate_theta_e(temperature: float, humidity: float, pressure: float) -> float:
    """
    Calculate Equivalent Potential Temperature (Theta-E) using Bolton's (1980) formula.
    
    Theta-E represents the temperature an air parcel would have if all its moisture
    were condensed out and the latent heat used to warm the parcel, then brought
    dry-adiabatically to 1000 hPa. It MUST be higher than ambient temperature
    because it includes latent heat of water vapor.
    
    For tropical conditions (T ≈ 30°C, RH ≈ 75%), Theta-E typically ranges
    from 335 K to 360 K.
    
    Reference: Bolton, D. (1980). Monthly Weather Review, 108(7), 1046-1053.
    """
    # 1. Convert ambient temperature to Kelvin
    T_k = temperature + 273.15
    
    # 2. Calculate dew point temperature in Kelvin
    # Using the Magnus-Tetens formula (consistent with calculate_dew_point)
    a = MAGNUS_A
    b = MAGNUS_B
    alpha = math.log(humidity / 100.0) + (a * temperature) / (b + temperature)
    Td_C = (b * alpha) / (a - alpha)
    Td_K = Td_C + 273.15
    
    # 3. Temperature at Lifting Condensation Level (Bolton 1980, Eq. 22)
    T_LCL = (1.0 / (1.0 / (Td_K - 56.0) + math.log(T_k / Td_K) / 800.0)) + 56.0
    
    # 4. Mixing ratio w (kg/kg) using saturation vapor pressure at dew point
    e = 6.112 * math.exp((17.67 * Td_C) / (Td_C + 243.5))
    w = 0.622 * e / (pressure - e)
    
    # 5. Equivalent potential temperature (Bolton 1980, Eq. 43)
    theta_e = T_k * math.pow(1000.0 / pressure, 0.2854 * (1.0 - 0.28 * w))
    theta_e *= math.exp(((3376.0 / T_LCL) - 2.54) * w * (1.0 + 0.81 * w))
    
    return round(theta_e, 1)


def calculate_li_proxy(temperature: float) -> float:
    """Calculate surface-based Lifted Index proxy."""
    T_env_5km = temperature - (6.5 * 5.0)
    T_parcel_5km = temperature - (9.8 * 5.0)
    li_proxy = T_env_5km - T_parcel_5km
    return round(li_proxy, 2)


def calculate_pressure_tendency(recent_pressures: list) -> tuple[Optional[float], Optional[str]]:
    """Calculate pressure tendency and classify it."""
    if len(recent_pressures) < 2:
        return None, None
    window = min(len(recent_pressures), 120)
    if window < 2:
        return None, None
    y = np.array(recent_pressures[-window:])
    x = np.arange(window)
    slope, _ = np.polyfit(x, y, 1)
    tendency = round(slope * 60, 2)
    label = classify_pressure_tendency(tendency)
    return tendency, label


def classify_pressure_tendency(tendency: float) -> str:
    """Classify pressure tendency into WMO-style categories."""
    if tendency > PRESSURE_THRESHOLDS["rising_rapidly"]:
        return "Rising rapidly"
    elif tendency > PRESSURE_THRESHOLDS["rising_slowly"]:
        return "Rising slowly"
    elif tendency >= PRESSURE_THRESHOLDS["steady_lower"]:
        return "Steady"
    elif tendency >= PRESSURE_THRESHOLDS["falling_slowly"]:
        return "Falling slowly"
    else:
        return "Falling rapidly"


def generate_alerts(
    temperature: float,
    humidity: float,
    dew_point_spread: float,
    pressure_tendency: Optional[float],
    pressure_label: Optional[str],
    li_proxy: float,
    theta_e_rising: Optional[bool]
) -> list[str]:
    """Generate plain-language weather alerts."""
    alerts = []

    if dew_point_spread < ALERT_THRESHOLDS["small_dew_spread"]:
        alert = "Dew point depression < 2\u00b0C: Fog or low cloud possible."
        if pressure_tendency is not None and pressure_tendency < 0:
            alert += " High moisture with falling pressure; watch for showers."
        alerts.append(alert)

    if li_proxy < ALERT_THRESHOLDS["unstable_LI"]:
        base_alert = f"LI proxy ({li_proxy}\u00b0C) indicates unstable atmosphere."
        if theta_e_rising:
            base_alert += " Theta-E is rising; potential for convective activity."
        alerts.append(base_alert)

    if (pressure_tendency is not None and
        pressure_tendency < PRESSURE_THRESHOLDS["falling_rapidly"] and
        humidity > ALERT_THRESHOLDS["high_humidity"]):
        alerts.append("Rapid pressure fall in moist air; possible storm development.")

    if (not alerts and
        dew_point_spread > ALERT_THRESHOLDS["large_dew_spread"] and
        pressure_label in ["Steady", "Rising slowly", "Rising rapidly"]):
        alerts.append("Stable conditions; no immediate weather hazard indicated.")

    return alerts if alerts else ["Conditions normal. No alerts at this time."]


def calculate_cape_proxy(temperature: float, humidity: float, pressure: float) -> dict:
    """Surface-based CAPE proxy estimation (adapted from Doswell & Rasmussen, 1994)."""
    es = 6.112 * math.exp((17.67 * temperature) / (temperature + 243.5))
    e = es * (humidity / 100.0)
    w = 0.622 * (e / (pressure - e))

    Tv = (temperature + 273.15) * (1 + 0.61 * w)
    env_T500 = Tv - 6.5 * 5.5
    parcel_T500 = Tv - 9.8 * 5.5

    buoyancy = parcel_T500 - env_T500
    cape_proxy = round(buoyancy * 500 if buoyancy > 0 else buoyancy * 200)

    if cape_proxy < 0:
        interpretation = "Stable. No convective energy available."
        level = "none"
    elif cape_proxy < 500:
        interpretation = "Marginal instability. Weak convection possible."
        level = "low"
    elif cape_proxy < 1500:
        interpretation = "Moderate instability. Scattered thunderstorms possible."
        level = "moderate"
    elif cape_proxy < 3000:
        interpretation = "High instability. Organized convection likely."
        level = "high"
    else:
        interpretation = "Extreme instability. Severe weather potential."
        level = "extreme"

    return {"cape_proxy": cape_proxy, "interpretation": interpretation, "level": level}


def calculate_convective_temperature(temperature: float, dew_point: float, humidity: float) -> dict:
    """Estimate surface temperature needed to trigger free convection."""
    spread = temperature - dew_point
    dryness_factor = (100 - humidity) / 100.0
    convective_temp = dew_point + spread * (1.2 + dryness_factor * 0.8)
    degrees_needed = round(convective_temp - temperature, 1)
    trigger_likely = degrees_needed < 3

    if trigger_likely:
        interpretation = (
            "Free convection already possible."
            if degrees_needed <= 0
            else f"Only {degrees_needed}\u00b0C warming needed. Convection likely."
        )
    else:
        interpretation = f"{degrees_needed}\u00b0C warming needed. Convection unlikely."

    return {
        "convective_temperature": round(convective_temp, 1),
        "trigger_likely": trigger_likely,
        "degrees_needed": degrees_needed,
        "interpretation": interpretation
    }


def estimate_rainfall_probability(
    humidity: float,
    dew_point_spread: float,
    pressure_tendency: float | None,
    li_proxy: float
) -> dict:
    """Multi-factor rainfall probability estimation."""
    score = 0

    if humidity > 90:
        score += 30
    elif humidity > 75:
        score += 20
    elif humidity > 60:
        score += 10

    if dew_point_spread < 1:
        score += 35
    elif dew_point_spread < 2:
        score += 25
    elif dew_point_spread < 4:
        score += 10

    if pressure_tendency is not None:
        if pressure_tendency < -1.5:
            score += 25
        elif pressure_tendency < -0.5:
            score += 15
        elif pressure_tendency < 0:
            score += 5

    if li_proxy < -3:
        score += 10
    elif li_proxy < -1:
        score += 5

    probability = min(score, 95)

    if probability < 25:
        category = "none"
        interpretation = "Rainfall unlikely under current conditions."
    elif probability < 50:
        category = "low"
        interpretation = "Isolated showers possible but not widespread."
    elif probability < 75:
        category = "moderate"
        interpretation = "Rainfall probable. Prepare for wet conditions."
    else:
        category = "high"
        interpretation = "Rainfall likely. Conditions favorable for precipitation."

    return {
        "probability": probability,
        "category": category,
        "interpretation": interpretation
    }