import { API_BASE_URL } from '../constants/config';

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export type HealthSummary = Record<string, number | null>;

export const healthApi = {
  getSummary: (hours = 24) => get<HealthSummary>(`/health/summary?hours=${hours}`),
  getLatest: (metric: string, limit = 5) =>
    get<{ value: number; timestamp: string }[]>(`/health/latest?metric=${metric}&limit=${limit}`),
  getTrend: (metric: string, days = 7) =>
    get<{ current: number; previous: number; delta: number }>(`/health/trend?metric=${metric}&days=${days}`),
};
