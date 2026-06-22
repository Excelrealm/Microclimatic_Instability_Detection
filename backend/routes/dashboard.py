"""
Endpoint for serving processed data to the web dashboard.
"""
import csv
import io

from fastapi import APIRouter, Query

from services.data_store import data_store
from models.atmospheric import ProcessedReading

router = APIRouter()


@router.get("/api/dashboard/current")
async def get_current_conditions():
    """
    Get the most recent atmospheric reading and derived indicators.
    """
    current = data_store.get_current()
    
    if current is None:
        return {
            "status": "no_data",
            "message": "No readings available yet",
            "data": None
        }
    
    return {
        "status": "success",
        "data": current
    }


@router.get("/api/dashboard/history")
async def get_reading_history(count: int = Query(default=120, le=1000)):
    """
    Get historical readings for chart display.
    
    Args:
        count: Number of recent readings to return (max 1000)
    """
    readings = data_store.get_recent(count)
    
    return {
        "status": "success",
        "count": len(readings),
        "data": readings
    }


@router.get("/api/dashboard/summary")
async def get_summary():
    """
    Get a summary of current atmospheric conditions.
    """
    current = data_store.get_current()
    
    if current is None:
        return {
            "status": "no_data",
            "message": "No data available for summary"
        }
    
    # Build summary
    summary = {
        "temperature": current.get("temperature"),
        "humidity": current.get("humidity"),
        "pressure": current.get("pressure"),
        "dew_point": current.get("dew_point"),
        "dew_point_spread": current.get("dew_point_spread"),
        "pressure_tendency": current.get("pressure_tendency_label", "N/A"),
        "li_proxy": current.get("li_proxy"),
        "theta_e": current.get("theta_e"),
        "alerts": current.get("alerts", [])
    }
    
    return {
        "status": "success",
        "summary": summary
    }

from fastapi.responses import StreamingResponse
import io

@router.get("/api/export/csv")
async def export_csv():
    """Export all stored readings as CSV."""
    readings = data_store._read_all()
    
    if not readings:
        return {"error": "No data available"}
    
    # Create CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=readings[0].keys())
    writer.writeheader()
    writer.writerows(readings)
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=readings.csv"}
    )