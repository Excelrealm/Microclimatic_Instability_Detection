import type { ProcessedReading } from '../types';
import './StatisticsPanel.css';

interface Props {
  historyData: ProcessedReading[];
}

function StatisticsPanel({ historyData }: Props) {
  if (!historyData || historyData.length < 2) return null;

  const stats = (values: number[]) => ({
    min: Math.min(...values).toFixed(1),
    max: Math.max(...values).toFixed(1),
    mean: (values.reduce((a, b) => a + b, 0) / values.length).toFixed(1),
  });

  const tempStats = stats(historyData.map((r) => r.temperature));
  const humStats = stats(historyData.map((r) => r.humidity));
  const pressStats = stats(historyData.map((r) => r.pressure));
  const dewStats = stats(historyData.map((r) => r.dew_point));

  const metrics = [
    { label: 'Temperature (°C)', ...tempStats },
    { label: 'Humidity (%)', ...humStats },
    { label: 'Pressure (hPa)', ...pressStats },
    { label: 'Dew Point (°C)', ...dewStats },
  ];

  return (
    <div className="statistics-panel">
      <h2>📊 Statistical Summary</h2>
      <p className="stat-subtitle">Based on {historyData.length} readings</p>
      <table className="stats-table">
        <thead>
          <tr>
            <th>Parameter</th>
            <th>Min</th>
            <th>Mean</th>
            <th>Max</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((m, i) => (
            <tr key={i}>
              <td>{m.label}</td>
              <td>{m.min}</td>
              <td className="mean-cell">{m.mean}</td>
              <td>{m.max}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default StatisticsPanel;