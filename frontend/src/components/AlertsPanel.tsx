import type { ProcessedReading } from '../types';
import './AlertsPanel.css';

interface Props {
  currentData: ProcessedReading | null;
}

function AlertsPanel({ currentData }: Props) {
  if (!currentData) return null;

  const { alerts } = currentData;

  function getAlertIcon(alert: string): string {
    if (alert.includes('Fog') || alert.includes('low cloud')) return '🌫️';
    if (alert.includes('storm') || alert.includes('convective')) return '⛈️';
    if (alert.includes('showers') || alert.includes('precipitation')) return '🌧️';
    if (alert.includes('unstable')) return '⚠️';
    if (alert.includes('Stable') || alert.includes('normal')) return '✅';
    return 'ℹ️';
  }

  function getAlertClass(alert: string): string {
    if (alert.includes('storm') || alert.includes('severe')) return 'severe';
    if (alert.includes('unstable') || alert.includes('convective')) return 'warning';
    if (alert.includes('Fog') || alert.includes('showers')) return 'moderate';
    return 'info';
  }

  return (
    <div className="alerts-panel">
      <h2>📋 Weather Alerts</h2>
      {alerts.length === 0 ? (
        <div className="no-alerts">
          <span>✅</span>
          <p>No active alerts. Conditions are normal.</p>
        </div>
      ) : (
        <div className="alerts-list">
          {alerts.map((alert, i) => (
            <div key={i} className={`alert-item ${getAlertClass(alert)}`}>
              <span className="alert-icon">{getAlertIcon(alert)}</span>
              <p className="alert-text">{alert}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default AlertsPanel;