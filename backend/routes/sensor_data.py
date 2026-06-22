"""
Endpoint for receiving sensor data from ESP32.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone, timedelta

from models.atmospheric import SensorReading, ProcessedReading
from services.data_processor import (
    calculate_dew_point,
    calculate_theta_e,
    calculate_li_proxy,
    calculate_pressure_tendency,
    generate_alerts,
    calculate_cape_proxy,
    calculate_convective_temperature,
    estimate_rainfall_probability,
)
from services.data_store import data_store
from utils.validators import validate_sensor_data
from services.anomaly_detector import anomaly_detector
from services.pattern_classifier import pattern_classifier
# Forecaster disabled — TensorFlow removed
# from services.forecaster import forecaster

router = APIRouter()


@router.post("/api/sensor-data")
async def receive_sensor_data(reading: SensorReading):
    """
    Receive atmospheric data from ESP32 sensor node.
    Process and store the reading with derived indicators.
    """
    # Validate the incoming data
    is_valid, error_message = validate_sensor_data(
        reading.temperature,
        reading.humidity,
        reading.pressure
    )

    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)

    # Calculate derived parameters
    dew_point = calculate_dew_point(reading.temperature, reading.humidity)
    dew_point_spread = round(reading.temperature - dew_point, 2)

    theta_e = calculate_theta_e(reading.temperature, reading.humidity, reading.pressure)
    li_proxy = calculate_li_proxy(reading.temperature)

    # Get pressure history for tendency calculation
    pressure_history = data_store.get_pressure_history()
    pressure_history.append(reading.pressure)

    pressure_tendency, pressure_label = calculate_pressure_tendency(pressure_history)

    # Check if Theta-E is rising
    theta_e_rising = None
    prev_reading = data_store.get_current()
    if prev_reading and "theta_e" in prev_reading:
        theta_e_rising = theta_e > prev_reading["theta_e"]

    # Generate alerts
    alerts = generate_alerts(
        temperature=reading.temperature,
        humidity=reading.humidity,
        dew_point_spread=dew_point_spread,
        pressure_tendency=pressure_tendency,
        pressure_label=pressure_label,
        li_proxy=li_proxy,
        theta_e_rising=theta_e_rising
    )

    # Atmospheric physics calculations
    cape_result = calculate_cape_proxy(reading.temperature, reading.humidity, reading.pressure)

    convective_result = calculate_convective_temperature(
        reading.temperature, dew_point, reading.humidity
    )

    rainfall_result = estimate_rainfall_probability(
        reading.humidity, dew_point_spread, pressure_tendency, li_proxy
    )

    # ─── AI-Powered Analysis ───────────────────────────────────

    reading_count = len(data_store._read_all())

    # 1. Anomaly Detection — train every 50 readings
    anomaly_detector.add_reading(
        reading.temperature, reading.humidity, reading.pressure,
        dew_point, li_proxy, theta_e
    )
    if reading_count % 50 == 0:
        anomaly_detector.train()
        anomaly_detector.save_model()

    anomaly_result = anomaly_detector.predict(
        reading.temperature, reading.humidity, reading.pressure,
        dew_point, li_proxy, theta_e
    )

    # 2. Pattern Classification — uses .predict() method (matches your classifier file)
    pattern_result = pattern_classifier.predict(
        reading.temperature, reading.humidity, reading.pressure,
        dew_point_spread, pressure_tendency, li_proxy,
        theta_e
    )

    # 3. Forecaster — disabled (TensorFlow removed)
    # forecaster.add_reading(reading.temperature, reading.humidity, reading.pressure)
    # if reading_count % 100 == 0 and reading_count > 0:
    #     forecaster.train()
    #     forecaster.save_model()

    # Create processed reading — Nigeria time (UTC+1)
    nigeria_tz = timezone(timedelta(hours=1))
    timestamp = datetime.now(nigeria_tz)

    processed = ProcessedReading(
        id=0,
        timestamp=timestamp.isoformat(),
        temperature=round(reading.temperature, 2),
        humidity=round(reading.humidity, 2),
        pressure=round(reading.pressure, 2),
        dew_point=dew_point,
        dew_point_spread=dew_point_spread,
        pressure_tendency=pressure_tendency,
        pressure_tendency_label=pressure_label,
        li_proxy=li_proxy,
        theta_e=theta_e,
        alerts=alerts,
        cape_proxy=cape_result["cape_proxy"],
        cape_level=cape_result["level"],
        cape_interpretation=cape_result["interpretation"],
        convective_temperature=convective_result["convective_temperature"],
        trigger_likely=convective_result["trigger_likely"],
        degrees_needed=convective_result["degrees_needed"],
        convective_interpretation=convective_result["interpretation"],
        rainfall_probability=rainfall_result["probability"],
        rainfall_category=rainfall_result["category"],
        rainfall_interpretation=rainfall_result["interpretation"],
        anomaly_detected=anomaly_result["is_anomaly"],
        anomaly_score=anomaly_result["score"],
        anomaly_message=anomaly_result["message"],
        pattern=pattern_result["pattern"],
        pattern_label=pattern_result["label"],
        pattern_confidence=pattern_result["confidence"],
        forecast_available=False,
        forecast_trend="",
        forecast_message="",
    )

    # Store the reading
    reading_id = data_store.add_reading(processed)
    processed.id = reading_id

    return {
        "status": "success",
        "message": "Data received and processed",
        "reading_id": reading_id,
        "data": processed
    }