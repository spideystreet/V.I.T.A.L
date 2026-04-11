import { useEffect, useState } from 'react';
import { healthApi, HealthSummary } from '../services/healthApi';

export function useHealthData(hours = 24) {
  const [data, setData] = useState<HealthSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const summary = await healthApi.getSummary(hours);
      setData(summary);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { refresh(); }, [hours]);

  return { data, loading, error, refresh };
}
