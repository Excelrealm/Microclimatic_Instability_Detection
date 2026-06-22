import { useState, useEffect } from 'react';
import axios from 'axios';
import './RainPredictionCard.css';

interface RainPrediction {
  rain_probability?: number;
  will_rain?: boolean;
  confidence?: string;
  timestamp?: string;
  error?: string;           // <-- add this
}

function RainPredictionCard() {
  const [data, setData] = useState<RainPrediction | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRain = async () => {
      try {
        const res = await axios.get<RainPrediction>('http://localhost:8000/api/predict/rainfall');
        setData(res.data);
        setError('');
      } catch {
        setError('Rain prediction unavailable');
      }
    };
    fetchRain();
    const interval = setInterval(fetchRain, 3600000); // every hour
    return () => clearInterval(interval);
  }, []);

  // Handle connection errors
  if (error && !data) {
    return (
      <div className="rain-card error">
        <p>{error}</p>
      </div>
    );
  }

  // Handle API error (model not loaded, not enough data, etc.)
  if (data?.error) {
    return (
      <div className="rain-card">
        <h3>🌧️ AI Rain Prediction</h3>
        <p>{data.error}</p>
      </div>
    );
  }

  // Loading state
  if (!data || data.rain_probability === undefined) {
    return (
      <div className="rain-card">
        <p>Loading rain prediction…</p>
      </div>
    );
  }

  const prob = data.rain_probability;
  const rainLikely = data.will_rain ?? false;
  const color = rainLikely ? '#dc3545' : '#28a745';

  return (
    <div className="rain-card">
      <h3>🌧️ AI Rain Prediction</h3>
      <div className="rain-probability">
        <span className="rain-value">{(prob * 100).toFixed(0)}%</span>
        <span className="rain-label" style={{ color }}>
          {rainLikely ? 'Rain Likely' : 'Dry'}
        </span>
      </div>
      <p className="rain-confidence">Confidence: {data.confidence ?? 'N/A'}</p>
      <p className="rain-timestamp">
        Updated: {data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : 'N/A'}
      </p>
    </div>
  );
}

export default RainPredictionCard;