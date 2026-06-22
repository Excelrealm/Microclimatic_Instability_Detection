import type { RemoteWeatherData } from '../services/api';
import './RemoteWeatherCard.css';

interface Props {
  data: RemoteWeatherData | null;
}

function RemoteWeatherCard({ data }: Props) {
  if (!data) return null;

  return (
    <div className="remote-weather-card">
      <h3>🌍 {data.location}</h3>
      <p className="remote-timestamp">
        Updated: {new Date(data.timestamp).toLocaleString('en-NG')}
      </p>
      <div className="remote-grid">
        <div className="remote-item">
          <span className="remote-icon">🌡️</span>
          <span className="remote-value">{data.temperature.toFixed(1)}°C</span>
        </div>
        <div className="remote-item">
          <span className="remote-icon">💧</span>
          <span className="remote-value">{data.humidity}%</span>
        </div>
        <div className="remote-item">
          <span className="remote-icon">📊</span>
          <span className="remote-value">{data.pressure.toFixed(1)} hPa</span>
        </div>
        <div className="remote-item">
          <span className="remote-icon">💨</span>
          <span className="remote-value">{data.windSpeed.toFixed(1)} km/h</span>
        </div>
      </div>
    </div>
  );
}

export default RemoteWeatherCard;