"""
Main FastAPI application for IoT-Based Microclimate Monitoring
and Atmospheric Instability Detection System.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Route imports
from routes.sensor_data import router as sensor_router
from routes.dashboard import router as dashboard_router
from routes.ai_routes import router as ai_router
from routes.predictions import router as predictions_router

# AI service imports (used in startup and health check)
from services.anomaly_detector import anomaly_detector
from services.pattern_classifier import pattern_classifier
# Forecaster disabled — TensorFlow removed due to protobuf version conflict
# from services.forecaster import forecaster

# Import ML prediction model loaders
from services.predictor import load_instability_models, load_rainfall_model

app = FastAPI(
    title="Microclimate Monitoring API",
    description="Backend for IoT-Based Microclimate Monitoring and Atmospheric Instability Detection System with AI Enhancement",
    version="2.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(sensor_router, tags=["Sensor Data"])
app.include_router(dashboard_router, tags=["Dashboard"])
app.include_router(ai_router, tags=["AI Features"])
app.include_router(predictions_router, tags=["ML Predictions"])


@app.on_event("startup")
async def startup_event():
    """Load AI models on application startup."""
    print("Loading AI models...")

    # Load anomaly and pattern models
    anomaly_detector.load_model()
    pattern_classifier.load_model()

    # Forecaster disabled (TensorFlow removed)
    # forecaster.load_model()

    # Load ML prediction models (instability & rainfall)
    load_instability_models()
    load_rainfall_model()

    print("AI models loaded successfully.")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "system": "Microclimate Monitoring API",
        "status": "running",
        "version": "2.0.0",
        "ai_features": {
            "anomaly_detection": anomaly_detector.is_trained,
            "pattern_classification": pattern_classifier.is_trained,
            "forecasting": False,  # Disabled
        },
    }