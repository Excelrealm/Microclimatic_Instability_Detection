"""Unsupervised anomaly detection using Isolation Forest."""

import numpy as np
from sklearn.ensemble import IsolationForest
import json
import os


class AtmosphericAnomalyDetector:
    def __init__(self, model_path: str = "data/anomaly_model.json"):
        self.model = IsolationForest(
            contamination=0.05, random_state=42, n_estimators=100
        )
        self.model_path = model_path
        self.is_trained = False
        self.training_data: list = []
        self.min_samples = 100

    def add_reading(self, temperature, humidity, pressure, dew_point, li_proxy, theta_e):
        self.training_data.append([temperature, humidity, pressure, dew_point, li_proxy, theta_e])
        if len(self.training_data) > 1000:
            self.training_data = self.training_data[-1000:]

    def train(self):
        if len(self.training_data) < self.min_samples:
            return False
        X = np.array(self.training_data)
        self.model.fit(X)
        self.is_trained = True
        return True

    def predict(self, temperature, humidity, pressure, dew_point, li_proxy, theta_e):
        if not self.is_trained:
            return {"is_anomaly": False, "score": 0.0, "message": "Model not yet trained."}
        X = np.array([[temperature, humidity, pressure, dew_point, li_proxy, theta_e]])
        prediction = self.model.predict(X)[0]
        score = float(self.model.decision_function(X)[0])
        is_anomaly = prediction == -1
        if is_anomaly:
            msg = "Significant anomaly detected." if score < -0.1 else "Mild anomaly detected."
        else:
            msg = "Conditions within normal range."
        return {"is_anomaly": is_anomaly, "score": round(score, 4), "message": msg}

    def save_model(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        with open(self.model_path, "w") as f:
            json.dump(self.training_data, f)

    def load_model(self):
        if os.path.exists(self.model_path):
            with open(self.model_path, "r") as f:
                self.training_data = json.load(f)
            if len(self.training_data) >= self.min_samples:
                self.train()
                return True
        return False


anomaly_detector = AtmosphericAnomalyDetector()