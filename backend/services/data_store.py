"""
Simple JSON-based data storage for sensor readings.
Replace with SQLite for production use.
"""

import json
import os
from datetime import datetime
from typing import Optional

from config import DATA_FILE, MAX_STORED_READINGS
from models.atmospheric import ProcessedReading


class DataStore:
    """
    File-based data storage for atmospheric readings.
    """
    
    def __init__(self):
        self.file_path = DATA_FILE
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """Create data file and directory if they don't exist."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    def _read_all(self) -> list:
        """Read all readings from file."""
        with open(self.file_path, 'r') as f:
            return json.load(f)
    
    def _write_all(self, readings: list):
        """Write all readings to file."""
        with open(self.file_path, 'w') as f:
            json.dump(readings, f, indent=2)
    
    def add_reading(self, reading) -> int:
        readings = self._read_all()
        reading_dict = reading.model_dump()
        
        # Use the actual length to assign the next ID
        reading_dict["id"] = len(readings) + 1
        
        # APPEND the new reading
        readings.append(reading_dict)
        
        # Trim if over max
        if len(readings) > MAX_STORED_READINGS:
            readings = readings[-MAX_STORED_READINGS:]
        
        self._write_all(readings)
        return reading_dict["id"]
    def get_recent(self, count: int = 60) -> list[dict]:
        """Get the most recent n readings."""
        readings = self._read_all()
        return readings[-count:]
    
    def get_current(self) -> Optional[dict]:
        """Get the most recent reading."""
        readings = self._read_all()
        return readings[-1] if readings else None
    
    def get_pressure_history(self, count: int = 120) -> list[float]:
        """Get recent pressure values for tendency calculation."""
        readings = self._read_all()
        recent = readings[-count:]
        return [r["pressure"] for r in recent]


# Singleton instance
data_store = DataStore()