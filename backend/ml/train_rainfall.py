"""
Train a simple rainfall predictor using downloaded CHIRPS data + Open-Meteo.
Run: python ml/train_rainfall.py
"""

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import joblib, requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# ---------- CONFIG ----------
LAT, LON = 6.67, 3.16
CHIRPS_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "chirps_ota_daily.csv")
START_DATE, END_DATE = "2023-01-01", "2024-12-30"

# ---------- 1. Load CHIRPS data ----------
chirps_df = pd.read_csv(CHIRPS_CSV, parse_dates=['date'], index_col='date')
# The column name might be 'Rainfall (mm)' or 'precipitation' – rename to 'chirps'
# Detect the column containing rainfall
rain_col = [c for c in chirps_df.columns if 'rain' in c.lower() or 'precipitation' in c.lower()]
if not rain_col:
    # fallback: assume the second column
    rain_col = [chirps_df.columns[1]]
chirps_df = chirps_df[rain_col]
chirps_df.columns = ['chirps']

# ---------- 2. Fetch daily atmospheric features from Open-Meteo ----------
def fetch_openmeteo_daily(lat, lon, start, end):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": start, "end_date": end,
        "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,"
                 "relative_humidity_2m_mean,surface_pressure_mean,"
                 "dewpoint_2m_mean",
        "timezone": "Africa/Lagos"
    }
    resp = requests.get(url, params=params).json()
    df = pd.DataFrame(resp['daily'])
    df['date'] = pd.to_datetime(df['time'])
    df = df.set_index('date')
    df = df.rename(columns={
        'temperature_2m_mean': 't2m_mean',
        'temperature_2m_max': 't2m_max',
        'temperature_2m_min': 't2m_min',
        'relative_humidity_2m_mean': 'rh_mean',
        'surface_pressure_mean': 'sp_mean',
        'dewpoint_2m_mean': 'dew_point_mean'
    })
    return df

print("Fetching atmospheric features from Open-Meteo...")
atmo_df = fetch_openmeteo_daily(LAT, LON, START_DATE, END_DATE)

# ---------- 3. Merge ----------
merged = atmo_df.join(chirps_df, how='inner')
merged['rain_today'] = (merged['chirps'] > 1).astype(int)

# ---------- 4. Feature engineering ----------
for lag in range(1, 4):
    merged[f't2m_mean_lag{lag}d'] = merged['t2m_mean'].shift(lag)
    merged[f'rh_mean_lag{lag}d'] = merged['rh_mean'].shift(lag)
    merged[f'dew_point_mean_lag{lag}d'] = merged['dew_point_mean'].shift(lag)
merged['pressure_tendency'] = merged['sp_mean'].diff()
merged = merged.dropna()

feature_cols = [c for c in merged.columns if 'lag' in c or c in [
    't2m_mean','rh_mean','sp_mean','dew_point_mean','pressure_tendency']]
X = merged[feature_cols]
y = merged['rain_today']

# Temporal split
split_idx = int(len(X)*0.8)
X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

model = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

os.makedirs('ml_models', exist_ok=True)
joblib.dump(model, 'ml_models/rainfall_predictor.pkl')
joblib.dump(feature_cols, 'ml_models/rainfall_features.pkl')
print("Rainfall predictor saved.")