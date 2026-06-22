import joblib
import pandas as pd
import numpy as np
import os
from services.data_store import data_store

# ---------- Absolute path to ml_models ----------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "ml", "ml_models")

# ---------- Instability models ----------
models = {}
feature_cols = []
models_loaded = False

def load_instability_models():
    global models, feature_cols, models_loaded
    try:
        for name in ["pressure", "humidity", "dewpoint_spread", "temperature"]:
            path = os.path.join(MODEL_DIR, f"{name}_rf.pkl")
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing {path}")
            models[name] = joblib.load(path)
        
        feature_path = os.path.join(MODEL_DIR, "feature_cols.pkl")
        if not os.path.exists(feature_path):
            raise FileNotFoundError(f"Missing {feature_path}")
        feature_cols = joblib.load(feature_path)
        
        models_loaded = True
        print(f"✅ Loaded {len(models)} instability models.")
    except Exception as e:
        print(f"❌ Could not load instability models: {e}")
        models_loaded = False

load_instability_models()

# ---------- Rainfall model ----------
rainfall_model = None
rainfall_features = None

def load_rainfall_model():
    global rainfall_model, rainfall_features
    try:
        model_path = os.path.join(MODEL_DIR, "rainfall_predictor.pkl")
        features_path = os.path.join(MODEL_DIR, "rainfall_features.pkl")
        if os.path.exists(model_path) and os.path.exists(features_path):
            rainfall_model = joblib.load(model_path)
            rainfall_features = joblib.load(features_path)
            print("✅ Rainfall predictor loaded.")
        else:
            print("⚠️ Rainfall predictor not found. Run train_rainfall.py first.")
    except Exception as e:
        print(f"❌ Could not load rainfall model: {e}")

load_rainfall_model()

# ---------- Feature computation for instability ----------
def compute_daily_features_instability():
    all_readings = data_store._read_all()
    if len(all_readings) < 60:
        return None
    
    df = pd.DataFrame(all_readings)
    df['timestamp'] = pd.to_datetime(df['timestamp'].str.replace(r'\+.*$', '', regex=True))
    df = df.set_index('timestamp').sort_index()

    hourly = df.resample('h').agg({
        'temperature': ['max', 'min', 'mean'],
        'humidity': 'mean',
        'pressure': 'mean',
        'dew_point': 'mean'
    })
    hourly.columns = ['t2m_max', 't2m_min', 't2m_mean', 'rh_mean', 'sp_mean', 'dew_point']
    hourly = hourly.dropna()

    if len(hourly) < 2:
        return None

    hourly['p1h'] = hourly['sp_mean'].diff().fillna(0)
    
    for lag in range(1, 4):
        hourly[f't2m_lag{lag}'] = hourly['t2m_mean'].shift(lag).fillna(hourly['t2m_mean'])

    try:
        rain_series = (df.resample('h')['rainfall_probability'].max() > 70).astype(int)
    except:
        rain_series = pd.Series([0] * len(hourly), index=hourly.index)
    
    for lag in range(1, 4):
        shifted = rain_series.shift(lag)
        hourly[f'rain_lag{lag}'] = shifted.reindex(hourly.index, fill_value=0)

    latest = hourly.iloc[-1:].copy()
    for col in feature_cols:
        if col not in latest.columns:
            latest[col] = 0
    return latest[feature_cols].fillna(0)

def predict_instability():
    if not models_loaded:
        return {"error": "Instability models not loaded. Run training first."}
    X = compute_daily_features_instability()
    if X is None:
        return {"error": "Not enough historical data. Need at least 1 hour of readings."}

    probs = {}
    for name, model in models.items():
        try:
            probs[name] = round(model.predict_proba(X)[0][1], 3)
        except:
            probs[name] = 0.0

    weights = {"pressure": 0.25, "humidity": 0.35, "dewpoint_spread": 0.25, "temperature": 0.15}
    composite = sum(probs[n] * weights[n] for n in probs)

    risk = "Low"
    if composite >= 0.55:
        risk = "High"
    elif composite >= 0.30:
        risk = "Moderate"

    return {
        "composite_instability_score": round(composite, 3),
        "risk_level": risk,
        "individual_probabilities": probs,
        "timestamp": pd.Timestamp.now().isoformat()
    }

# ---------- Feature computation for rainfall ----------
def compute_daily_features_rainfall():
    all_readings = data_store._read_all()
    if len(all_readings) < 60:
        return None
    
    df = pd.DataFrame(all_readings)
    df['timestamp'] = pd.to_datetime(df['timestamp'].str.replace(r'\+.*$', '', regex=True))
    df = df.set_index('timestamp').sort_index()

    hourly = df.resample('h').agg({
        'temperature': 'mean',
        'humidity': 'mean',
        'pressure': 'mean',
        'dew_point': 'mean'
    })
    hourly.columns = ['t2m_mean', 'rh_mean', 'sp_mean', 'dew_point_mean']
    hourly = hourly.dropna()

    if len(hourly) < 2:
        return None

    hourly['pressure_tendency'] = hourly['sp_mean'].diff().fillna(0)
    
    for lag in range(1, 4):
        hourly[f't2m_mean_lag{lag}d'] = hourly['t2m_mean'].shift(lag).fillna(hourly['t2m_mean'])
        hourly[f'rh_mean_lag{lag}d'] = hourly['rh_mean'].shift(lag).fillna(hourly['rh_mean'])
        hourly[f'dew_point_mean_lag{lag}d'] = hourly['dew_point_mean'].shift(lag).fillna(hourly['dew_point_mean'])

    latest = hourly.iloc[-1:].copy()
    for col in rainfall_features:
        if col not in latest.columns:
            latest[col] = 0
    return latest[rainfall_features].fillna(0)

def predict_rainfall():
    if rainfall_model is None or rainfall_features is None:
        return {"error": "Rainfall model not loaded. Run train_rainfall.py first."}
    X = compute_daily_features_rainfall()
    if X is None:
        return {"error": "Not enough historical data. Need at least 1 hour of readings."}

    prob = round(float(rainfall_model.predict_proba(X)[0][1]), 3)
    return {
        "rain_probability": prob,
        "will_rain": prob > 0.5,
        "confidence": "high" if prob > 0.8 or prob < 0.2 else "moderate",
        "timestamp": pd.Timestamp.now().isoformat()
    }
    