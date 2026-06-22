import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  type ChartData,
  type ChartOptions,
  type TooltipItem,
} from 'chart.js';
import { CHART_COLORS } from '../config';
import type { ProcessedReading } from '../types';
import './TrendCharts.css';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

interface Props {
  historyData: ProcessedReading[];
}

function TrendCharts({ historyData }: Props) {
  if (!historyData || historyData.length === 0) {
    return (
      <div className="trend-charts">
        <h2>Trends &amp; Analysis</h2>
        <div className="no-data-message">
          <p>📈 Collecting data for trend analysis...</p>
          <p className="sub-text">Charts will appear once sufficient readings are available</p>
        </div>
      </div>
    );
  }

  const labels: string[] = historyData.map((reading) => {
    const date = new Date(reading.timestamp);
    return date.toLocaleTimeString('en-NG', { hour: '2-digit', minute: '2-digit' });
  });

  const tempData: number[] = historyData.map((r) => r.temperature);
  const humidityData: number[] = historyData.map((r) => r.humidity);
  const pressureData: number[] = historyData.map((r) => r.pressure);
  const dewPointData: number[] = historyData.map((r) => r.dew_point);
  const thetaEData: number[] = historyData.map((r) => r.theta_e);

  function createChartData(
    label: string,
    data: number[],
    colors: { border: string; background: string }
  ): ChartData<'line'> {
    return {
      labels,
      datasets: [{
        label,
        data,
        borderColor: colors.border,
        backgroundColor: colors.background,
        borderWidth: 2,
        fill: true,
        tension: 0.4,
        pointRadius: 1,
        pointHoverRadius: 5,
      }],
    };
  }

  function createChartOptions(unit: string, yMin: number, yMax: number): ChartOptions<'line'> {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top' as const,
          labels: { usePointStyle: true, padding: 15, font: { size: 11 } },
        },
                tooltip: {
          callbacks: {
            label: (context: TooltipItem<'line'>) => {
              const value = context.parsed.y;
              if (value === null || value === undefined) return 'No data';
              return `${value.toFixed(1)} ${unit}`;
            },
          },
        },
    },
      scales: {
        y: {
          min: yMin,
          max: yMax,
          ticks: { callback: (value: string | number) => `${value}${unit}`, font: { size: 10 } },
        },
        x: {
          ticks: { maxTicksLimit: 12, font: { size: 10 } },
        },
      },
    };
  }

  function getRange(data: number[], pad: number): [number, number] {
    return [Math.floor(Math.min(...data) - pad), Math.ceil(Math.max(...data) + pad)];
  }

  const [tMin, tMax] = getRange(tempData, 2);
  const [hMin, hMax] = getRange(humidityData, 5);
  const [pMin, pMax] = getRange(pressureData, 2);
  const [dMin, dMax] = getRange(dewPointData, 2);
  const [eMin, eMax] = getRange(thetaEData, 2);

  return (
    <div className="trend-charts">
      <h2>Trends &amp; Analysis</h2>
      <div className="charts-grid">
        <div className="chart-card">
          <h3>🌡️ Temperature</h3>
          <div className="chart-container">
            <Line data={createChartData('Temperature', tempData, CHART_COLORS.temperature)} options={createChartOptions('°C', tMin, tMax)} />
          </div>
        </div>
        <div className="chart-card">
          <h3>💧 Humidity</h3>
          <div className="chart-container">
            <Line data={createChartData('Humidity', humidityData, CHART_COLORS.humidity)} options={createChartOptions('%', hMin, hMax)} />
          </div>
        </div>
        <div className="chart-card">
          <h3>📊 Atmospheric Pressure</h3>
          <div className="chart-container">
            <Line data={createChartData('Pressure', pressureData, CHART_COLORS.pressure)} options={createChartOptions(' hPa', pMin, pMax)} />
          </div>
        </div>
        <div className="chart-card">
          <h3>🌫️ Dew Point Temperature</h3>
          <div className="chart-container">
            <Line data={createChartData('Dew Point', dewPointData, CHART_COLORS.dewPoint)} options={createChartOptions('°C', dMin, dMax)} />
          </div>
        </div>
        <div className="chart-card full-width">
          <h3>🔥 Equivalent Potential Temperature (Theta-E)</h3>
          <div className="chart-container">
            <Line data={createChartData('Theta-E', thetaEData, CHART_COLORS.thetaE)} options={createChartOptions(' K', eMin, eMax)} />
          </div>
        </div>
      </div>
    </div>
  );
}

export default TrendCharts;