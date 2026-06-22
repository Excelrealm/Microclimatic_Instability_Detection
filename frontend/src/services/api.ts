import axios from 'axios';
import { API_ENDPOINTS } from '../config';
import type { ApiResponse, HistoryApiResponse, ProcessedReading } from '../types';

export const fetchCurrentConditions = async (): Promise<ApiResponse<ProcessedReading | null>> => {
  const response = await axios.get<ApiResponse<ProcessedReading | null>>(API_ENDPOINTS.CURRENT);
  return response.data;
};

export const fetchHistory = async (count: number = 120): Promise<HistoryApiResponse> => {
  const response = await axios.get<HistoryApiResponse>(`${API_ENDPOINTS.HISTORY}?count=${count}`);
  return response.data;
};

// Remote Weather
const OPEN_METEO_BASE = 'https://api.open-meteo.com/v1/forecast';

export interface RemoteWeatherData {
  temperature: number;
  humidity: number;
  pressure: number;
  windSpeed: number;
  location: string;
  timestamp: string;
}

export const fetchRemoteWeather = async (latitude: number, longitude: number, locationName: string): Promise<RemoteWeatherData> => {
  const response = await axios.get(OPEN_METEO_BASE, {
    params: { latitude, longitude, current: 'temperature_2m,relative_humidity_2m,surface_pressure,wind_speed_10m', timezone: 'Africa/Lagos' },
  });
  const c = response.data.current;
  return { temperature: c.temperature_2m, humidity: c.relative_humidity_2m, pressure: c.surface_pressure, windSpeed: c.wind_speed_10m, location: locationName, timestamp: c.time };
};

// ─── Air Quality Data (Open-Meteo — free, no API key) ─────────────

export interface AirQualityData {
  timestamp: string;
  pm2_5: number;
  pm10: number;
  carbon_monoxide: number;
  nitrogen_dioxide: number;
  sulphur_dioxide: number;
  ozone: number;
  european_aqi: number;
  aqi_category: string;
}

export const fetchAirQuality = async (): Promise<AirQualityData> => {
  const response = await axios.get(
    'https://air-quality-api.open-meteo.com/v1/air-quality',
    {
      params: {
        latitude: 6.67,
        longitude: 3.16,
        current: 'european_aqi,pm2_5,pm10,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone',
      },
    }
  );

  const current = response.data.current;

  const aqi = current.european_aqi;
  let aqiCategory = 'Unknown';
  if (aqi <= 20) aqiCategory = 'Good';
  else if (aqi <= 40) aqiCategory = 'Fair';
  else if (aqi <= 60) aqiCategory = 'Moderate';
  else if (aqi <= 80) aqiCategory = 'Poor';
  else if (aqi <= 100) aqiCategory = 'Very Poor';
  else aqiCategory = 'Extremely Poor';

  return {
    timestamp: current.time,
    pm2_5: current.pm2_5 ?? 0,
    pm10: current.pm10 ?? 0,
    carbon_monoxide: current.carbon_monoxide ?? 0,
    nitrogen_dioxide: current.nitrogen_dioxide ?? 0,
    sulphur_dioxide: current.sulphur_dioxide ?? 0,
    ozone: current.ozone ?? 0,
    european_aqi: aqi,
    aqi_category: aqiCategory,
  };
};