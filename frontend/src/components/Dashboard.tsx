import { useState, useEffect, useCallback } from 'react';
import { fetchCurrentConditions, fetchHistory } from '../services/api';
import type { RemoteWeatherData } from '../services/api';
import { REFRESH_INTERVAL } from '../config';
import type { ProcessedReading } from '../types';
import CurrentConditions from './CurrentConditions';
import TrendCharts from './TrendCharts';
import InstabilityPanel from './InstabilityPanel';
import AlertsPanel from './AlertsPanel';
import LocationSelector from './LocationSelector';
import RemoteWeatherCard from './RemoteWeatherCard';
import StatusBadge from './StatusBadge';
import ExportButton from './ExportButton';
import StatisticsPanel from './StatisticsPanel';
import RefreshTimer from './RefreshTimer';
import MLInstabilityCard from './MLInstabilityCard';
import RainPredictionCard from './RainPredictionCard';
import RainfallCard from './RainfallCard';
import './Dashboard.css';

function Dashboard() {
  const [currentData, setCurrentData] = useState<ProcessedReading | null>(null);
  const [historyData, setHistoryData] = useState<ProcessedReading[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [remoteData, setRemoteData] = useState<RemoteWeatherData | null>(null);

  const loadData = useCallback(async () => {
    try {
      const currentResponse = await fetchCurrentConditions();
      if (currentResponse.status === 'success' && currentResponse.data) {
        setCurrentData(currentResponse.data);
        setLastUpdated(new Date());
        setError(null);
      } else {
        setCurrentData(null);
        setError(null);
      }

      const historyResponse = await fetchHistory(120);
      if (historyResponse.status === 'success') {
        setHistoryData(historyResponse.data);
      }
    } catch (err: unknown) {
      const axiosError = err as { code?: string };
      if (axiosError.code === 'ERR_NETWORK') {
        setError('Cannot connect to backend. Ensure the FastAPI server is running on port 8000.');
      } else {
        setError('Failed to load atmospheric data. Check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [loadData]);

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner" />
        <h2>Loading Atmospheric Data</h2>
        <p>Connecting to microclimate monitoring system...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <StatusBadge />
      {lastUpdated && (
        <div className="last-updated">
          Last updated: {lastUpdated.toLocaleTimeString('en-NG')}
          <span className="auto-refresh"> (<RefreshTimer />)</span>
        </div>
      )}

      {error && (
        <div className="error-banner">
          <span>⚠️</span> {error}
          <button onClick={loadData} className="retry-btn" type="button">Retry</button>
        </div>
      )}

      <div className="dashboard-grid">
        <div className="dashboard-main">
          <CurrentConditions currentData={currentData} />
          <StatisticsPanel historyData={historyData} />

          <div className="trend-charts">
            <div className="trends-header">
              <h2>Trends &amp; Analysis</h2>
              <ExportButton historyData={historyData} />
            </div>
            <TrendCharts historyData={historyData} />
          </div>
        </div>

        <div className="dashboard-sidebar">
          <RainfallCard currentData={currentData} />
          <RainPredictionCard />
          <LocationSelector onWeatherReceived={setRemoteData} />
          <RemoteWeatherCard data={remoteData} />
          <MLInstabilityCard />
          <AlertsPanel currentData={currentData} />
          <InstabilityPanel currentData={currentData} />
        </div>
      </div>
    </div>
  );
}


export default Dashboard;