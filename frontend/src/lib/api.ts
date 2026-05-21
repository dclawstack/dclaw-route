const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });
  if (!response.ok) {
    const error = await response.text();
    throw new ApiError(`API error ${response.status}: ${error}`, response.status);
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export const api = fetchJson;

export async function getHealth() {
  return fetchJson<{ status: string }>("/health/");
}

// ── Domain types (mirror backend Pydantic schemas) ──
export interface Stop {
  id: string;
  name: string;
  address: string;
  lat: number;
  lng: number;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Driver {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  vehicle_type: string;
  status: string;
  current_lat: number | null;
  current_lng: number | null;
  location_updated_at: string | null;
  created_at: string;
}

export interface Delivery {
  id: string;
  route_id: string;
  stop_id: string;
  sequence: number;
  status: string;
  notes: string | null;
  completed_at: string | null;
  created_at: string;
}

export interface Route {
  id: string;
  name: string;
  driver_id: string | null;
  status: string;
  total_distance_km: number;
  estimated_minutes: number;
  created_at: string;
  deliveries: Delivery[];
}

// ── Typed CRUD wrappers ──
export const stopsApi = {
  list: () => fetchJson<Stop[]>("/api/v1/stops/"),
  create: (data: Omit<Stop, "id" | "created_at" | "updated_at">) =>
    fetchJson<Stop>("/api/v1/stops/", { method: "POST", body: JSON.stringify(data) }),
  remove: (id: string) =>
    fetchJson<void>(`/api/v1/stops/${id}`, { method: "DELETE" }),
};

export const driversApi = {
  list: () => fetchJson<Driver[]>("/api/v1/drivers/"),
  create: (data: Pick<Driver, "name" | "email"> & Partial<Driver>) =>
    fetchJson<Driver>("/api/v1/drivers/", { method: "POST", body: JSON.stringify(data) }),
  remove: (id: string) =>
    fetchJson<void>(`/api/v1/drivers/${id}`, { method: "DELETE" }),
};

export interface OptimizeResult {
  route_id: string;
  original_sequence: string[];
  optimized_sequence: string[];
  original_distance_km: number;
  optimized_distance_km: number;
  improvement_percent: number;
}

export const routesApi = {
  list: () => fetchJson<Route[]>("/api/v1/routes/"),
  get: (id: string) => fetchJson<Route>(`/api/v1/routes/${id}`),
  create: (data: { name: string; driver_id?: string | null; stop_ids?: string[] }) =>
    fetchJson<Route>("/api/v1/routes/", { method: "POST", body: JSON.stringify(data) }),
  update: (id: string, data: Partial<Route>) =>
    fetchJson<Route>(`/api/v1/routes/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: string) =>
    fetchJson<void>(`/api/v1/routes/${id}`, { method: "DELETE" }),
  optimize: (id: string, max_stops?: number) =>
    fetchJson<OptimizeResult>(`/api/v1/routes/${id}/optimize`, {
      method: "POST",
      body: JSON.stringify({ max_stops: max_stops ?? null }),
    }),
};

export const deliveriesApi = {
  list: (routeId?: string) =>
    fetchJson<Delivery[]>(`/api/v1/deliveries/${routeId ? `?route_id=${routeId}` : ""}`),
  update: (id: string, data: Partial<Delivery>) =>
    fetchJson<Delivery>(`/api/v1/deliveries/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
};

export interface StopETA {
  delivery_id: string;
  stop_id: string;
  stop_name: string;
  sequence: number;
  distance_from_previous_km: number;
  cumulative_km: number;
  eta: string;
  minutes_from_now: number;
}

export interface RouteETA {
  route_id: string;
  driver_id: string | null;
  driver_position: [number, number] | null;
  stops: StopETA[];
  is_delayed: boolean;
}

export const trackingApi = {
  pushLocation: (driverId: string, lat: number, lng: number) =>
    fetchJson<{
      driver_id: string;
      current_lat: number;
      current_lng: number;
      location_updated_at: string;
    }>(`/api/v1/tracking/drivers/${driverId}/location`, {
      method: "POST",
      body: JSON.stringify({ lat, lng }),
    }),
  routeEta: (routeId: string) =>
    fetchJson<RouteETA>(`/api/v1/tracking/routes/${routeId}/eta`),
};
