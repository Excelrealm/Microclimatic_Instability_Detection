const API_BASE_URL = 'https://microclimatic-instability-detection.onrender.com';

export const API_ENDPOINTS = {
  CURRENT: `${API_BASE_URL}/api/dashboard/current`,
  HISTORY: `${API_BASE_URL}/api/dashboard/history`,
  AI_CHAT: `${API_BASE_URL}/api/ai/chat`,
} as const;

export const REFRESH_INTERVAL = 60000;

interface ChartColor {
  border: string;
  background: string;
}

export const CHART_COLORS: Record<string, ChartColor> = {
  temperature: { border: 'rgb(255, 99, 71)', background: 'rgba(255, 99, 71, 0.1)' },
  humidity: { border: 'rgb(54, 162, 235)', background: 'rgba(54, 162, 235, 0.1)' },
  pressure: { border: 'rgb(75, 192, 75)', background: 'rgba(75, 192, 75, 0.1)' },
  dewPoint: { border: 'rgb(153, 102, 255)', background: 'rgba(153, 102, 255, 0.1)' },
  thetaE: { border: 'rgb(255, 159, 64)', background: 'rgba(255, 159, 64, 0.1)' },
};