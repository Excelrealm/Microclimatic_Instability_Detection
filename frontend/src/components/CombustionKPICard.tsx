import { useState, useEffect } from 'react';
import { fetchAirQuality } from '../services/api';
import type { AirQualityData } from '../services/api';
import './CombustionKPICard.css';

function CombustionKPICard() {
  const [data, setData] = useState<AirQualityData | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetch = async () => {
      try {
        const result = await fetchAirQuality();
        setData(result);
        setError('');
      } catch {
        setError('Air quality data unavailable');
      }
    };
    fetch();
    const interval = setInterval(fetch, 1800000); // every 30 minutes
    return () => clearInterval(interval);
  }, []);

  if (error && !data) {
    return (
      <div className="combustion-kpi-card">
        <h3>🔥 Combustion Indicators</h3>
        <p className="error-text">{error}</p>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="combustion-kpi-card">
        <h3>🔥 Combustion Indicators</h3>
        <p>Loading air quality data...</p>
      </div>
    );
  }

  const getAQIColor = (aqi: number) => {
    if (aqi <= 20) return '#28a745';
    if (aqi <= 40) return '#4caf50';
    if (aqi <= 60) return '#ffc107';
    if (aqi <= 80) return '#ff9800';
    return '#dc3545';
  };

  const getCOLevel = (co: number) => {
    if (co < 200) return { label: 'Low', color: '#28a745' };
    if (co < 500) return { label: 'Moderate', color: '#ffc107' };
    return { label: 'High', color: '#dc3545' };
  };

  const coLevel = getCOLevel(data.carbon_monoxide);

  return (
    <div className="combustion-kpi-card">
      <h3>🔥 Combustion Indicators</h3>
      <p className="data-source">Source: Open-Meteo Air Quality</p>

      <div className="aqi-main">
        <span className="aqi-value" style={{ color: getAQIColor(data.european_aqi) }}>
          {data.european_aqi}
        </span>
        <span className="aqi-label">European AQI — {data.aqi_category}</span>
      </div>

      <div className="combustion-grid">
        <div className="combustion-item">
          <span className="combustion-icon">🛢️</span>
          <span className="combustion-name">CO</span>
          <span className="combustion-value">{data.carbon_monoxide.toFixed(0)} µg/m³</span>
          <span className="combustion-level" style={{ color: coLevel.color }}>{coLevel.label}</span>
        </div>

        <div className="combustion-item">
          <span className="combustion-icon">🏭</span>
          <span className="combustion-name">NO₂</span>
          <span className="combustion-value">{data.nitrogen_dioxide.toFixed(1)} µg/m³</span>
        </div>

        <div className="combustion-item">
          <span className="combustion-icon">🌫️</span>
          <span className="combustion-name">PM2.5</span>
          <span className="combustion-value">{data.pm2_5.toFixed(1)} µg/m³</span>
        </div>

        <div className="combustion-item">
          <span className="combustion-icon">🌫️</span>
          <span className="combustion-name">PM10</span>
          <span className="combustion-value">{data.pm10.toFixed(1)} µg/m³</span>
        </div>

        <div className="combustion-item">
          <span className="combustion-icon">☀️</span>
          <span className="combustion-name">O₃</span>
          <span className="combustion-value">{data.ozone.toFixed(1)} µg/m³</span>
        </div>

        <div className="combustion-item">
          <span className="combustion-icon">⚗️</span>
          <span className="combustion-name">SO₂</span>
          <span className="combustion-value">{data.sulphur_dioxide.toFixed(1)} µg/m³</span>
        </div>
      </div>
    </div>
  );
}

export default CombustionKPICard;