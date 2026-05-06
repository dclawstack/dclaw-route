export interface RoutePlan {
  id: string;
  stops: string[];
  optimized_sequence: string[];
  total_distance_km: number;
  estimated_time_minutes: number;
  fuel_cost: number;
  created_at: string;
}

export interface Waypoint {
  lat: number;
  lng: number;
  name: string;
}

export async function api<T>(
  path: string,
  init: RequestInit = {}
): Promise<T> {
  const url = `/api/v1${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(init.headers as Record<string, string>),
  };

  const res = await fetch(url, {
    ...init,
    headers,
  });

  if (!res.ok) {
    const text = await res.text().catch(() => "Unknown error");
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return res.json() as Promise<T>;
}
