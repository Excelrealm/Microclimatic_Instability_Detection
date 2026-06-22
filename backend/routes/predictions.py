from fastapi import APIRouter
from services.predictor import predict_instability, predict_rainfall

router = APIRouter()

@router.get("/api/predict/instability")
async def get_instability_prediction():
    return predict_instability()

@router.get("/api/predict/rainfall")
async def get_rainfall_prediction():
    return predict_rainfall()