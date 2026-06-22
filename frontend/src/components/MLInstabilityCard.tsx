import { useState, useEffect } from 'react';
import axios from 'axios';
import './MLInstabilityCard.css';

interface Prediction {
  composite_instability_score?: number;
  risk_level?: string;
  individual_probabilities?: Record<string, number>;
  timestamp?: string;
  error?: string;
}

function MLInstabilityCard() {
  const [data, setData] = useState<Prediction | null>(null);
  const [fetchError, setFetchError] = useState('');

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await axios.get<Prediction>('http://localhost:8000/api/predict/instability');
        setData(res.data);
        setFetchError('');
      } catch {
        setFetchError('ML prediction service unreachable');
      }
    };
    fetch();
    const interval = setInterval(fetch, 3600000);
    return () => clearInterval(interval);
  }, []);

  // Network / server down
  if (fetchError && !data) {
    return (
      <div className="ml-card error">
        <h3>🤖 ML Instability Assessment</h3>
        <p>{fetchError}</p>
      </div>
    );
  }

  // No data at all yet (still loading)
  if (!data) {
    return (
      <div className="ml-card">
        <h3>🤖 ML Instability Assessment</h3>
        <p>Loading prediction…</p>
      </div>
    );
  }

  // API returned an error (not enough data, models not loaded, etc.)
  if (data.error) {
    return (
      <div className="ml-card">
        <h3>🤖 ML Instability Assessment</h3>
        <p>{data.error}</p>
      </div>
    );
  }

  // Safe values with fallbacks
  const score =
    typeof data.composite_instability_score === 'number'
      ? data.composite_instability_score
      : 0;
  const risk = data.risk_level ?? 'Unknown';
  const probs = data.individual_probabilities ?? {};

  const riskColor =
    risk === 'High' ? '#dc3545' : risk === 'Moderate' ? '#ffc107' : '#28a745';

  return (
    <div className="ml-card">
      <h3>🤖 ML Instability Assessment</h3>
      <div className="composite-score">
        <span className="score-value">{score.toFixed(2)}</span>
        <span className="risk-badge" style={{ background: riskColor }}>
          {risk}
        </span>
      </div>
      <div className="individual-bars">
        {Object.keys(probs).length > 0 ? (
          Object.entries(probs).map(([key, prob]) => {
            const p = typeof prob === 'number' ? prob : 0;
            return (
              <div key={key} className="bar-item">
                <span className="bar-label">{key.replace('_', ' ')}</span>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{ width: `${(p * 100).toFixed(0)}%` }}
                  />
                </div>
                <span className="bar-value">{(p * 100).toFixed(0)}%</span>
              </div>
            );
          })
        ) : (
          <p>No probability data available.</p>
        )}
      </div>
      <p className="timestamp">
        Last updated:{' '}
        {data.timestamp
          ? new Date(data.timestamp).toLocaleTimeString()
          : 'N/A'}
      </p>
    </div>
  );
}

export default MLInstabilityCard;