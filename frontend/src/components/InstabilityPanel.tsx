import type { ProcessedReading } from '../types';
import './InstabilityPanel.css';

interface Props {
  currentData: ProcessedReading | null;
}

type StatusColor = 'danger' | 'warning' | 'success';

interface Status {
  label: string;
  color: StatusColor;
  icon: string;
}

interface Indicator extends Status {
  name: string;
  value: string;
  description: string;
}

function InstabilityPanel({ currentData }: Props) {
  if (!currentData) return null;

  const { dew_point_spread, li_proxy, theta_e, pressure_tendency_label } = currentData;

  function getDewSpreadStatus(spread: number): Status {
    if (spread < 2) return { label: 'Saturated', color: 'danger', icon: '🌧️' };
    if (spread < 5) return { label: 'Moderate', color: 'warning', icon: '⛅' };
    return { label: 'Dry', color: 'success', icon: '☀️' };
  }

  function getLIStatus(li: number): Status {
    if (li < -3) return { label: 'Very Unstable', color: 'danger', icon: '⛈️' };
    if (li < -1) return { label: 'Marginally Unstable', color: 'warning', icon: '🌤️' };
    return { label: 'Stable', color: 'success', icon: '☀️' };
  }

  function getThetaEStatus(te: number): Status {
    if (te > 350) return { label: 'High Energy', color: 'danger', icon: '🔥' };
    if (te > 330) return { label: 'Moderate Energy', color: 'warning', icon: '🌡️' };
    return { label: 'Low Energy', color: 'success', icon: '❄️' };
  }

  const dewStatus = getDewSpreadStatus(dew_point_spread);
  const liStatus = getLIStatus(li_proxy);
  const thetaStatus = getThetaEStatus(theta_e);

  const indicators: Indicator[] = [
    {
      name: 'Dew Point Spread',
      value: `${dew_point_spread.toFixed(1)}°C`,
      ...dewStatus,
      description: dew_point_spread < 2
        ? 'Air is nearly saturated. Fog or precipitation likely.'
        : dew_point_spread < 5
        ? 'Moderate moisture content in the atmosphere.'
        : 'Dry air mass. Stable conditions expected.',
    },
    {
      name: 'Lifted Index (Proxy)',
      value: `${li_proxy.toFixed(1)}°C`,
      ...liStatus,
      description: li_proxy < -3
        ? 'Strong instability. Potential for severe convection.'
        : li_proxy < -1
        ? 'Marginal instability. Watch for shower development.'
        : 'Stable atmosphere. Convection unlikely.',
    },
    {
      name: 'Theta-E',
      value: `${theta_e.toFixed(1)} K`,
      ...thetaStatus,
      description: theta_e > 350
        ? 'High moist static energy. Favorable for deep convection.'
        : theta_e > 330
        ? 'Moderate energy available in the boundary layer.'
        : 'Limited energy. Atmosphere is relatively stable.',
    },
  ];

  return (
    <div className="instability-panel">
      <h2>⚡ Instability Indicators</h2>
      <div className="indicators-grid">
        {indicators.map((ind, i) => (
          <div key={i} className={`indicator-card ${ind.color}`}>
            <div className="indicator-header">
              <span className="indicator-icon">{ind.icon}</span>
              <div>
                <div className="indicator-name">{ind.name}</div>
                <div className="indicator-value">{ind.value}</div>
              </div>
              <span className={`status-badge ${ind.color}`}>{ind.label}</span>
            </div>
            <p className="indicator-description">{ind.description}</p>
          </div>
        ))}
      </div>
      {pressure_tendency_label && (
        <div className="pressure-trend-summary">
          <span className="trend-icon">📊</span>
          <span>Pressure Trend: <strong>{pressure_tendency_label}</strong></span>
        </div>
      )}
    </div>
  );
}

export default InstabilityPanel;