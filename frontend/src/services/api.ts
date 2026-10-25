export interface HealthData {
  status: string;
  service: string;
  environment: string;
  version: string;
  timestamp: string;
  database: {
    status: string;
    engine: string;
    latency_ms: number;
  };
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export async function fetchHealthTelemetry(): Promise<HealthData> {
  const response = await fetch(`${API_BASE_URL}/health`);
  if (!response.ok) {
    throw new Error(`Health probe failed with status ${response.status}`);
  }
  return response.json();
}
