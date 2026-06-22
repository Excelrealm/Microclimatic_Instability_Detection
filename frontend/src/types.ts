export interface ProcessedReading {
  id: number;
  timestamp: string;
  temperature: number;
  humidity: number;
  pressure: number;
  dew_point: number;
  dew_point_spread: number;
  pressure_tendency: number | null;
  pressure_tendency_label: string | null;
  li_proxy: number;
  theta_e: number;
  alerts: string[];
  cape_proxy: number;
  cape_level: string;
  cape_interpretation: string;
  convective_temperature: number;
  trigger_likely: boolean;
  degrees_needed: number;
  convective_interpretation: string;
  rainfall_probability: number;
  rainfall_category: string;
  rainfall_interpretation: string;
  anomaly_detected: boolean;
  anomaly_score: number;
  anomaly_message: string;
  pattern: string;
  pattern_label: string;
  pattern_confidence: number;
  forecast_available: boolean;
  forecast_trend: string;
  forecast_message: string;
}

export interface ApiResponse<T> {
  status: string;
  message?: string;
  data: T;
}

export interface HistoryApiResponse {
  status: string;
  count: number;
  data: ProcessedReading[];
}