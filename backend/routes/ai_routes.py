"""
API endpoints for AI-powered features:
- Anomaly detection
- Pattern classification
- Time-series forecasting
- AI Chat assistant
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from services.data_store import data_store
from services.anomaly_detector import anomaly_detector
from services.pattern_classifier import pattern_classifier
from services.forecaster import forecaster
from services.ai_assistant import ask_weather_assistant, get_weather_summary

router = APIRouter(prefix="/api/ai")


# ─── Request Models ────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str
    include_current_data: bool = True


class LabelSampleRequest(BaseModel):
    temperature: float
    humidity: float
    pressure: float
    dew_point_spread: float
    pressure_tendency: Optional[float] = None
    li_proxy: float
    theta_e: float
    pattern: str  # One of: clear_dry, partly_cloudy, overcast, foggy, pre_convective, thunderstorm_risk


# ─── Chat Endpoints ────────────────────────────────────────────

@router.post("/chat")
async def chat_with_assistant(request: ChatRequest):
    """Chat with the AI weather assistant."""
    current_data = None
    if request.include_current_data:
        current_data = data_store.get_current()

    result = ask_weather_assistant(request.question, current_data)

    return {
        "status": "success" if result["success"] else "error",
        "question": request.question,
        "answer": result["answer"],
        "model": result.get("model", "unknown"),
        "data_used": current_data is not None,
    }


@router.get("/summary")
async def get_ai_summary():
    """Get an AI-generated summary of current conditions."""
    current_data = data_store.get_current()
    if not current_data:
        return {
            "status": "no_data",
            "summary": "No data available yet.",
        }

    summary = get_weather_summary(current_data)
    return {
        "status": "success",
        "summary": summary,
    }


# ─── Anomaly Detection Endpoints ───────────────────────────────

@router.get("/anomaly/status")
async def get_anomaly_status():
    """Get the current anomaly detection status."""
    current = data_store.get_current()
    if not current:
        return {"status": "no_data", "trained": anomaly_detector.is_trained}

    return {
        "status": "success",
        "trained": anomaly_detector.is_trained,
        "samples_collected": len(anomaly_detector.training_data),
        "min_samples_needed": anomaly_detector.min_samples,
    }


# ─── Pattern Classification Endpoints ──────────────────────────

@router.get("/pattern/status")
async def get_pattern_status():
    """Get pattern classifier training status."""
    return {
        "status": "success",
        "trained": pattern_classifier.is_trained,
        "labeled_samples": len(pattern_classifier.X_train),
        "patterns_available": pattern_classifier.PATTERNS,
        "method": "ml_classifier" if pattern_classifier.is_trained else "rule_based",
    }


@router.post("/pattern/label")
async def label_weather_sample(request: LabelSampleRequest):
    """Submit a labeled weather observation for training."""
    pattern_classifier.add_labeled_sample(
        temperature=request.temperature,
        humidity=request.humidity,
        pressure=request.pressure,
        dew_point_spread=request.dew_point_spread,
        pressure_tendency=request.pressure_tendency,
        li_proxy=request.li_proxy,
        theta_e=request.theta_e,
        pattern=request.pattern,
    )

    # Try to train if enough data
    trained = pattern_classifier.train()
    if trained:
        pattern_classifier.save_model()

    return {
        "status": "success",
        "message": "Sample added",
        "total_samples": len(pattern_classifier.X_train),
        "model_trained": trained,
    }


# ─── Forecasting Endpoints ─────────────────────────────────────

@router.get("/forecast")
async def get_forecast():
    """Get AI-generated forecast for next hour."""
    if not forecaster.is_trained:
        return {
            "status": "not_ready",
            "message": "Forecaster needs more training data.",
            "samples_collected": len(forecaster.training_data),
            "min_samples_needed": forecaster.min_samples,
        }

    forecast = forecaster.predict()
    if forecast is None:
        return {"status": "error", "message": "Forecast unavailable."}

    return {
        "status": "success",
        "forecast": forecast["forecasts"],
        "horizon_minutes": forecast["horizon_minutes"],
    }


@router.get("/forecast/status")
async def get_forecast_status():
    """Get forecaster training status."""
    return {
        "status": "success",
        "trained": forecaster.is_trained,
        "tensorflow_available": "tensorflow" in str(type(forecaster.model)) if forecaster.model else False,
        "samples_collected": len(forecaster.training_data),
        "min_samples_needed": forecaster.min_samples,
    }