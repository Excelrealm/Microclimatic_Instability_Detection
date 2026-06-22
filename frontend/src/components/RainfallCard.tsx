import type { ProcessedReading } from '../types';
import './RainfallCard.css';

interface Props {
  currentData: ProcessedReading | null;
}

function RainfallCard({ currentData }: Props) {
  if (!currentData) return null;

  const { rainfall_probability, rainfall_category, rainfall_interpretation } = currentData;

  const getColor = (prob: number) => {
    if (prob >= 75) return '#dc3545';  // red — high
    if (prob >= 50) return '#ffc107';  // amber — moderate
    if (prob >= 25) return '#17a2b8';  // blue — low
    return '#28a745';                   // green — none
  };

  const getIcon = (prob: number) => {
    if (prob >= 75) return '🌧️';
    if (prob >= 50) return '🌦️';
    if (prob >= 25) return '🌤️';
    return '☀️';
  };

  const color = getColor(rainfall_probability);

  return (
    <div className="rainfall-card" style={{ borderLeft: `4px solid ${color}` }}>
      <h3>{getIcon(rainfall_probability)} Rainfall Probability</h3>
      <div className="rainfall-score">
        <span className="rainfall-value" style={{ color }}>{rainfall_probability}%</span>
        <span className="rainfall-category" style={{ background: color }}>{rainfall_category}</span>
      </div>
      <p className="rainfall-interpretation">{rainfall_interpretation}</p>
    </div>
  );
}

export default RainfallCard;