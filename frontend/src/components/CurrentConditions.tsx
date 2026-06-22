import type { ProcessedReading } from '../types';
import './CurrentConditions.css';

interface Props {
  currentData: ProcessedReading | null;
}

function CurrentConditions({ currentData }: Props) {
  if (!currentData) {
    return (
      <div className="current-conditions">
        <h2>Current Conditions</h2>
        <div className="no-data-message">
          <p>⏳ Waiting for sensor data...</p>
          <p className="sub-text">Ensure the ESP32 is running and sending readings</p>
        </div>
      </div>
    );
  }

  const {
    temperature,
    humidity,
    pressure,
    dew_point,
    dew_point_spread,
    pressure_tendency_label,
    li_proxy,
    theta_e,
  } = currentData;

  const tempClass =
    temperature >= 35 ? 'hot' :
    temperature >= 25 ? 'warm' :
    temperature >= 15 ? 'mild' :
    'cool';

  const humidityClass =
    humidity >= 80 ? 'high' :
    humidity >= 50 ? 'moderate' :
    'low';

  return (
    <div className="current-conditions">
      <h2>Current Conditions</h2>
      <div className="conditions-grid">

        <div className={`condition-card primary ${tempClass}`}>
          <div className="card-icon">🌡️</div>
          <div className="card-label">Temperature</div>
          <div className="card-value">{temperature.toFixed(1)}°C</div>
        </div>

        <div className={`condition-card primary ${humidityClass}`}>
          <div className="card-icon">💧</div>
          <div className="card-label">Humidity</div>
          <div className="card-value">{humidity.toFixed(1)}%</div>
        </div>

        <div className="condition-card primary-trend">
          <div className="card-icon">📊</div>
          <div className="card-label">Pressure</div>
          <div className="card-value">{pressure.toFixed(1)} hPa</div>
          <div className="pressure-trend">{pressure_tendency_label || 'Steady'}</div>
        </div>

        <div className="condition-card derived">
          <div className="card-icon">🌫️</div>
          <div className="card-label">Dew Point</div>
          <div className="card-value">{dew_point.toFixed(1)}°C</div>
          <div className="card-sub">Spread: {dew_point_spread.toFixed(1)}°C</div>
        </div>

        <div className="condition-card derived">
          <div className="card-icon">⚡</div>
          <div className="card-label">LI Proxy</div>
          <div className="card-value">{li_proxy.toFixed(1)}°C</div>
          <div className={`card-sub ${li_proxy < -2 ? 'unstable' : 'stable'}`}>
            {li_proxy < -2 ? '⚠️ Unstable' : '✓ Stable'}
          </div>
        </div>

        <div className="condition-card derived">
          <div className="card-icon">🔥</div>
          <div className="card-label">Theta-E</div>
          <div className="card-value">{theta_e.toFixed(1)} K</div>
          <div className="card-sub">Moist static energy</div>
        </div>

      </div>
    </div>
  );
}

export default CurrentConditions;