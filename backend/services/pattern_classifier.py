"""Weather pattern classification using Random Forest with rule-based fallback."""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle
import os
from typing import Optional


class WeatherPatternClassifier:
    PATTERNS = ["clear_dry", "partly_cloudy", "overcast", "foggy", "pre_convective", "thunderstorm_risk"]
    PATTERN_LABELS = {
        "clear_dry": "Clear & Dry",
        "partly_cloudy": "Partly Cloudy",
        "overcast": "Overcast",
        "foggy": "Foggy/Hazy",
        "pre_convective": "Pre-Convective",
        "thunderstorm_risk": "Thunderstorm Risk",
    }

    def __init__(self, model_path: str = "data/pattern_classifier.pkl"):
        self.model = RandomForestClassifier(n_estimators=50, max_depth=8, random_state=42, class_weight="balanced")
        self.scaler = StandardScaler()
        self.model_path = model_path
        self.is_trained = False
        self.X_train: list = []
        self.y_train: list = []

    def add_labeled_sample(self, temperature, humidity, pressure, dew_point_spread, pressure_tendency, li_proxy, theta_e, pattern):
        self.X_train.append([temperature, humidity, pressure, dew_point_spread, pressure_tendency or 0, li_proxy, theta_e])
        self.y_train.append(pattern)

    def train(self):
        if len(self.X_train) < 30:
            return False
        X = np.array(self.X_train)
        y = np.array(self.y_train)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.is_trained = True
        return True

    def predict(self, temperature, humidity, pressure, dew_point_spread, pressure_tendency, li_proxy, theta_e):
        if not self.is_trained:
            return self._rule_based(temperature, humidity, pressure, dew_point_spread, pressure_tendency, li_proxy, theta_e)
        X = np.array([[temperature, humidity, pressure, dew_point_spread, pressure_tendency or 0, li_proxy, theta_e]])
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)[0]
        proba = self.model.predict_proba(X_scaled)[0]
        return {"pattern": prediction, "label": self.PATTERN_LABELS.get(prediction, prediction), "confidence": round(float(max(proba)), 2), "method": "ml"}

    def _rule_based(self, temperature, humidity, pressure, dew_point_spread, pressure_tendency, li_proxy, theta_e):
        if li_proxy < -2 and humidity > 70 and pressure_tendency is not None and pressure_tendency < -0.5:
            p = "thunderstorm_risk"
        elif dew_point_spread < 2:
            p = "foggy"
        elif li_proxy < -1 and theta_e > 340:
            p = "pre_convective"
        elif humidity > 80:
            p = "overcast"
        elif humidity > 50:
            p = "partly_cloudy"
        else:
            p = "clear_dry"
        return {"pattern": p, "label": self.PATTERN_LABELS.get(p, p), "confidence": 0.6, "method": "rule"}

    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "wb") as f:
            pickle.dump({"model": self.model, "scaler": self.scaler, "X_train": self.X_train, "y_train": self.y_train, "is_trained": self.is_trained}, f)

    def load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as f:
                data = pickle.load(f)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.X_train = data["X_train"]
            self.y_train = data["y_train"]
            self.is_trained = data["is_trained"]
            return True
        return False


pattern_classifier = WeatherPatternClassifier()