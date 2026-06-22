#type: ignore
"""
LSTM time-series forecasting for microclimate data.
NOTE: Currently disabled due to TensorFlow protobuf version conflict.
All functionality is safely wrapped — import errors are caught.
"""

import numpy as np
import os
import json

try:
    from tensorflow.keras.models import Sequential, load_model
    from tensorflow.keras.layers import LSTM, Dense, Dropout
    from tensorflow.keras.callbacks import EarlyStopping
    import tensorflow as tf
    tf.get_logger().setLevel("ERROR")
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class MicroclimateForecaster:
    def __init__(self, model_path: str = "data/lstm_forecaster.keras", lookback: int = 24, forecast_horizon: int = 6):
        self.lookback = lookback
        self.forecast_horizon = forecast_horizon
        self.model_path = model_path
        self.model = None
        self.is_trained = False
        self.training_data: list = []
        self.min_samples = lookback + forecast_horizon + 50
        self.mean = None
        self.std = None
        if TENSORFLOW_AVAILABLE:
            try:
                self._build_model()
            except Exception:
                pass

    def _build_model(self):
        if not TENSORFLOW_AVAILABLE:
            return
        self.model = Sequential([
            LSTM(32, input_shape=(self.lookback, 3), return_sequences=True),
            Dropout(0.2),
            LSTM(16, return_sequences=False),
            Dropout(0.2),
            Dense(self.forecast_horizon * 3),
        ])
        self.model.compile(optimizer="adam", loss="mse")

    def add_reading(self, temperature, humidity, pressure):
        self.training_data.append([temperature, humidity, pressure])
        if len(self.training_data) > 2000:
            self.training_data = self.training_data[-2000:]

    def _prepare_sequences(self):
        if not TENSORFLOW_AVAILABLE:
            return None, None
        data = np.array(self.training_data)
        self.mean = data.mean(axis=0)
        self.std = data.std(axis=0) + 1e-8
        data_norm = (data - self.mean) / self.std
        X, y = [], []
        for i in range(len(data_norm) - self.lookback - self.forecast_horizon + 1):
            X.append(data_norm[i:i + self.lookback])
            y.append(data_norm[i + self.lookback:i + self.lookback + self.forecast_horizon].flatten())
        return np.array(X), np.array(y)

    def train(self):
        if not TENSORFLOW_AVAILABLE or len(self.training_data) < self.min_samples:
            return False
        X, y = self._prepare_sequences()
        if X is None or len(X) < 10:
            return False
        try:
            self._build_model()
            self.model.fit(
                X, y,
                epochs=30,
                batch_size=16,
                validation_split=0.2,
                callbacks=[EarlyStopping(patience=5, restore_best_weights=True)],
                verbose=0
            )
            self.is_trained = True
            return True
        except Exception:
            return False

    def predict(self):
        if not TENSORFLOW_AVAILABLE or not self.is_trained:
            return None
        try:
            data = np.array(self.training_data)
            data_norm = (data - self.mean) / self.std
            X = data_norm[-self.lookback:].reshape(1, self.lookback, 3)
            pred = self.model.predict(X, verbose=0)[0].reshape(self.forecast_horizon, 3)
            pred = pred * self.std + self.mean
            forecasts = []
            for i in range(self.forecast_horizon):
                forecasts.append({
                    "step": i + 1,
                    "temperature": round(float(pred[i, 0]), 1),
                    "humidity": max(0, min(100, round(float(pred[i, 1]), 1))),
                    "pressure": round(float(pred[i, 2]), 1),
                })
            return {"forecasts": forecasts, "horizon_minutes": self.forecast_horizon}
        except Exception:
            return None

    def save_model(self):
        if not TENSORFLOW_AVAILABLE or self.model is None:
            return
        try:
            os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
            self.model.save(self.model_path)
            with open(self.model_path.replace(".keras", "_params.json"), "w") as f:
                json.dump({"mean": self.mean.tolist(), "std": self.std.tolist()}, f)
        except Exception:
            pass

    def load_model(self):
        if not TENSORFLOW_AVAILABLE:
            return False
        try:
            if os.path.exists(self.model_path):
                self.model = load_model(self.model_path)
                params_path = self.model_path.replace(".keras", "_params.json")
                if os.path.exists(params_path):
                    with open(params_path, "r") as f:
                        p = json.load(f)
                    self.mean = np.array(p["mean"])
                    self.std = np.array(p["std"])
                self.is_trained = True
                return True
        except Exception:
            pass
        return False


forecaster = MicroclimateForecaster()