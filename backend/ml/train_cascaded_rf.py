"""
Train cascaded Random Forest instability predictors.
"""
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import joblib, requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

LAT, LON = 6.67, 3.16
CHIRPS_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "chirps_ota_daily.csv")
START_DATE, END_DATE = "2023-01-01", "2024-12-30"

# Load CHIRPS
chirps_df = pd.read_csv(CHIRPS_CSV, parse_dates=['date'], index_col='date')
rain_col = [c for c in chirps_df.columns if 'rain' in c.lower() or 'precipitation' in c.lower()]
if not rain_col: rain_col = [chirps_df.columns[1]]
chirps_df = chirps_df[rain_col]; chirps_df.columns = ['chirps']

# Fetch Open-Meteo daily
def fetch_ometeo(lat,lon,start,end):
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat, "longitude": lon,
        "start_date": start, "end_date": end,
        "daily": "temperature_2m_mean,temperature_2m_max,temperature_2m_min,"
                 "relative_humidity_2m_mean,surface_pressure_mean,"
                 "dewpoint_2m_mean,precipitation_sum",
        "timezone": "Africa/Lagos"
    }
    resp = requests.get(url, params=params).json()
    df = pd.DataFrame(resp['daily'])
    df['date'] = pd.to_datetime(df['time'])
    df = df.set_index('date')
    df = df.rename(columns={
        'temperature_2m_mean':'t2m_mean',
        'temperature_2m_max':'t2m_max',
        'temperature_2m_min':'t2m_min',
        'relative_humidity_2m_mean':'rh_mean',
        'surface_pressure_mean':'sp_mean',
        'dewpoint_2m_mean':'dew_point_mean',
        'precipitation_sum':'ometeo_rain'
    })
    return df

print("Fetching Open-Meteo daily...")
df = fetch_ometeo(LAT, LON, START_DATE, END_DATE)
# Merge with CHIRPS for a consistent rain indicator (use ometeo_rain for lag, but we need actual rain for train)
df['rain_obs'] = chirps_df['chirps'].reindex(df.index, fill_value=0)
df['rain_today'] = (df['rain_obs'] > 1).astype(int)

# Build features
df['p24h'] = df['sp_mean'].diff()
# Dew point spread: approximation using Magnus on daily mean
df['dew_point'] = df.apply(
    lambda row: (243.12 * (np.log(row.rh_mean/100) + (17.62*row.t2m_mean)/(243.12+row.t2m_mean))) /
                (17.62 - (np.log(row.rh_mean/100) + (17.62*row.t2m_mean)/(243.12+row.t2m_mean))),
    axis=1)
df['dew_spread'] = df['t2m_mean'] - df['dew_point']

# Lagged features
for lag in range(1,4):
    df[f't2m_lag{lag}'] = df['t2m_mean'].shift(lag)
    df[f'rain_lag{lag}'] = df['rain_today'].shift(lag)

df = df.dropna()

# Targets
df['target_pressure'] = (df['p24h'] <= -0.5).astype(int)       # 24h pressure fall
df['target_humidity'] = ((df['rh_mean'] - df['rh_mean'].shift(1)) >= 8.0).astype(int)
df['target_dewspread'] = (df['dew_spread'] <= 2.0).astype(int)
df['target_tempdrop'] = ((df['t2m_max'] - df['t2m_min']) >= 2.0).astype(int)  # simplified temp drop

feature_cols = ['t2m_max','t2m_min','rh_mean','sp_mean','dew_point','p24h',
                't2m_lag1','t2m_lag2','t2m_lag3',
                'rain_lag1','rain_lag2','rain_lag3']

targets = {
    'pressure': 'target_pressure',
    'humidity': 'target_humidity',
    'dewpoint_spread': 'target_dewspread',
    'temperature': 'target_tempdrop'
}

os.makedirs('ml_models', exist_ok=True)
for name, tcol in targets.items():
    X = df[feature_cols]
    y = df[tcol]
    split_idx = int(len(X)*0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]
    rf = RandomForestClassifier(n_estimators=100, max_depth=8, min_samples_split=5, random_state=42)
    rf.fit(X_train, y_train)
    y_pred = rf.predict(X_test)
    print(f"\n=== {name} ===")
    print(classification_report(y_test, y_pred))
    joblib.dump(rf, f'ml_models/{name}_rf.pkl')

joblib.dump(feature_cols, 'ml_models/feature_cols.pkl')
print("Cascaded models saved.")