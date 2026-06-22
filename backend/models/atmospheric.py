"""
Pydantic models for atmospheric data validation and response formatting.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class SensorReading(BaseModel):
    """
    Incoming sensor data from ESP32.
    """
    temperature: float = Field(..., ge=-50, le=90, description="Temperature in °C")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity in %")
    pressure: float = Field(..., ge=200, le=1200, description="Atmospheric pressure in hPa")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ProcessedReading(BaseModel):
    id: int
    timestamp: str
    temperature: float
    humidity: float
    pressure: float
    dew_point: float
    dew_point_spread: float
    pressure_tendency: Optional[float] = None
    pressure_tendency_label: Optional[str] = None
    li_proxy: float
    theta_e: float
    alerts: list[str] = []
    
    # New fields
    cape_proxy: float = 0
    cape_level: str = "none"
    cape_interpretation: str = ""
    convective_temperature: float = 0
    trigger_likely: bool = False
    degrees_needed: float = 0
    convective_interpretation: str = ""
    rainfall_probability: int = 0
    rainfall_category: str = "none"
    rainfall_interpretation: str = ""


class DashboardResponse(BaseModel):
    """
    Complete dashboard data payload.
    """
    current: Optional[ProcessedReading] = None
    recent_readings: list[ProcessedReading] = []
    summary: dict = {}